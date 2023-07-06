import pandas as pd
from flask_caching import Cache
import hashlib
import pickle
import copy
from ...util import getenv # noqa

# Configure cache
LAYOUT_CACHE_TIMEOUT = int(getenv("DASH_LAYOUT_CACHE_TIMEOUT", 86400))
SERVICES_CACHE_TIMEOUT = int(getenv("DASH_SERVICES_CACHE_TIMEOUT", 86400))

layout_cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "/tmp/cache-directory/layout",
        "CACHE_DEFAULT_TIMEOUT": LAYOUT_CACHE_TIMEOUT,
    },
)
services_slow_cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "/tmp/cache-directory/services",
        "CACHE_DEFAULT_TIMEOUT": SERVICES_CACHE_TIMEOUT,
    },
)
services_fast_cache = Cache(
    config={
        "CACHE_TYPE": "SimpleCache",
    },
)


def key_hash(key: str):
    """Hashes a string"""
    m = hashlib.sha256()
    m.update(key.encode("utf-8"))
    return m.hexdigest()


class KeyCacheable():
    """A base class that enabe extending classes to use the cache decorators"""
    def __init__(self, commands=[], cache=services_slow_cache):
        self.cache_key: str = None
        self.cache = cache
        self.commands = commands.copy()
        if commands:
            self.cache_key = commands[-1]["key"]

    def copy(self):
        return self.__class__(copy.deepcopy(self.commands))

    def add_command(self, is_final_command, takes_input, func, *args):
        """Adds a command to the command list

        Arguments:
        is_final_command: Is the function should return directly the result
        takes_input: Should we pass an input to the function
        func: The function to be executed
        args: The function's arguments
        """
        serialized_kwargs = pickle.dumps(args)
        start = f"{self.cache_key}_" if self.cache_key else ""
        self.cache_key = f"{start}{func.__name__}_{serialized_kwargs}"
        hash = key_hash(self.cache_key)

        self.commands.append({
            "func": func,
            "args": args,
            "hash": hash,
            "key": self.cache_key,
            "is_final_command": is_final_command,
            "takes_input": takes_input
        })

    def get_most_recent_cached_result(self):
        """ Returns the index of the latest command with a cached result """
        idx = len(self.commands) - 1
        res = None
        while idx >= 0:
            command = self.commands[idx]
            res = self.cache.get(command["hash"])
            if res is not None:
                break
            idx = idx - 1

        return res, idx

    def resolve(self):
        """Resolves the command list"""

        # Get the most precise cached command
        res, idx = self.get_most_recent_cached_result()

        # Resolve the rest without cache
        while idx + 1 < len(self.commands):
            idx = idx + 1
            command = self.commands[idx]

            if command["takes_input"]:
                res = command["func"](self, res, *command["args"])
            else:
                res = command["func"](self, *command["args"])

            # Cache the results
            self.cache.set(command["hash"], res)

        return res


def cached_command(is_final_command, takes_input):
    """Decorates a class method to put it in a command list"""
    def inner(func):
        def wrapper(self: KeyCacheable, *args):
            self.add_command(is_final_command, takes_input,  func, *args)
            if not is_final_command:
                return self
            else:
                return self.resolve()
        return wrapper
    return inner


def final_cached_command():
    """Decorates a method to be cached. The method returns the result immediately"""
    return cached_command(is_final_command=True, takes_input=True)


def chained_cached_command():
    """Decorates a method to be cached. The method returns the class instance"""
    return cached_command(is_final_command=False, takes_input=True)


def single_cached_command():
    """Decorates a method to be cached. The method returns the result immediately and does not take inputs"""
    return cached_command(is_final_command=True, takes_input=False)


class DfCacheable(KeyCacheable):
    """ Contains a few basic df manipulation commands"""
    @chained_cached_command()
    def date_range(self, df, date_column, begin, end):
        """Adds a date range filter"""
        if end is not None:
            df = df[
                (df[date_column] <= end)
            ]
        if begin is not None:
            df = df[
                (df[date_column] > begin)
            ]
        return df

    def date_agg(self, date_column, freq):
        if freq == "daily":
            return self.daily_agg(date_column)
        elif freq == "monthly":
            return self.monthly_agg(date_column)
        else:
            raise Exception("Unknown date aggregation frequency")

    @chained_cached_command()
    def daily_agg(self, df, columns):
        if not type(columns) == list:
            columns = [columns]
        date_column = columns[0]
        """Adds an aggregation by day"""
        df = self.date_manipulations(df, date_column, "daily")
        df = df.groupby(columns)
        return df

    @chained_cached_command()
    def monthly_agg(self, df, columns):
        """Adds an aggregation by month"""
        if not type(columns) == list:
            columns = [columns]
        date_column = columns[0]
        df = self.date_manipulations(df, date_column, "monthly")
        df = df.groupby(columns)
        return df

    @final_cached_command()
    def agg(self, df, column, operators):
        """Sums results, works also on aggregations"""
        res = (
            df[column]
            .agg(list(operators.keys()))
            .reset_index()
            .rename(columns=operators)
        )
        return res

    @final_cached_command()
    def sum(self, df, column):
        """Sums results, works also on aggregations"""
        res = df[column].sum()

        # Reset index if we are computing aggregated sums
        if type(res) == pd.core.series.Series:
            res = res.reset_index()

        return res

    @final_cached_command()
    def sum_over_time(self, df, date_column, column, freq):
        df = self.date_manipulations(df, date_column, freq)
        df = df.sort_values(by=date_column, ascending=True)
        df[column] = df[column].cumsum()
        return df

    @final_cached_command()
    def cumsum(self, df, column):
        """Cumulative sum"""
        return df[column].cumsum()

    def date_manipulations(self, df, date_column, freq):
        if freq == "daily":
            return self.date_manipulations_daily(df, date_column)
        elif freq == "monthly":
            return self.date_manipulations_monthly(df, date_column)

    def date_manipulations_monthly(self, df, date_column):
        df[date_column] = pd.to_datetime(df[date_column]).dt.to_period("M")
        return df

    def date_manipulations_daily(self, df, date_column):
        if not (df.empty):
            # TODO: dates should already in date format
            df[date_column] = (
                df[date_column]
                .dt.tz_localize(None)
                .dt.floor("D")
                .dt.date
            )
            datelist = pd.date_range(
                start=df[date_column].min() + pd.DateOffset(-1),
                end=pd.to_datetime("today"),
                freq="D",
            )
            df_date = pd.DataFrame()
            df_date["Date_continous"] = datelist
            df_date["Date_continous"] = (
                pd.to_datetime(df_date["Date_continous"], unit="s")
                .dt.tz_localize(None)
                .dt.floor("D")
                .dt.date
            )
            df = df.merge(
                df_date, how="right", left_on=date_column, right_on="Date_continous"
            ).reset_index(drop=True)
            df[date_column] = df["Date_continous"]
            for i in df.columns:
                if "Quantity" in i:
                    df[i] = df[i].fillna(0)
                if "Amount" in i:
                    df[i] = df[i].fillna(0)
                else:
                    df[i] = df[i].fillna("missing")
                    df[i] = df[i].replace("", "missing")
        return df
