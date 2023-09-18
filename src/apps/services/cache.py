import pandas as pd
import datetime
from flask_caching import Cache
import hashlib
import pickle
import copy
from .helpers import DashArgumentException
from ...util import getenv # noqa

# Configure cache
LAYOUT_CACHE_TIMEOUT = int(getenv("DASH_LAYOUT_CACHE_TIMEOUT", 86400))
SERVICES_SLOW_CACHE_TIMEOUT = int(getenv("DASH_SERVICES_SLOW_CACHE_TIMEOUT", 86400))
SERVICES_FAST_CACHE_TIMEOUT = int(getenv("DASH_SERVICES_FAST_CACHE_TIMEOUT", 60))

layout_cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "/tmp/cache-directory/layout",
        "CACHE_DEFAULT_TIMEOUT": LAYOUT_CACHE_TIMEOUT,
    },
)
services_long_cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "/tmp/cache-directory/services",
        "CACHE_DEFAULT_TIMEOUT": SERVICES_SLOW_CACHE_TIMEOUT,
    },
)
services_short_cache = Cache(
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": SERVICES_FAST_CACHE_TIMEOUT
    },
)


def init_app(app):
    services_long_cache.init_app(app)
    services_short_cache.init_app(app)
    layout_cache.init_app(app)


def key_hash(key: str):
    """Hashes a string"""
    m = hashlib.sha256()
    m.update(key.encode("utf-8"))
    return m.hexdigest()


class KeyCacheable():
    """A base class that enabe extending classes to use the cache decorators"""
    def __init__(self, commands=[], cache=services_long_cache):
        self.cache_key: str = self.__class__.__name__
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
    def date_range(self, df: pd.DataFrame, date_column: str, begin: datetime.datetime, end: datetime.datetime):
        """Adds a date range filter"""
        def convert_date(date):
            if isinstance(df[date_column][0], datetime.date):
                date = datetime.date(date.year, date.month, date.day)
            return date
        if df.empty:
            return df
        if end is not None:
            df = df[
                (df[date_column] <= convert_date(end))
            ]
        if begin is not None:
            df = df[
                (df[date_column] >= convert_date(begin))
            ]
        return df

    def date_agg_uncached(self, df, date_column, freq):
        if freq == "daily":
            return self.daily_agg(df, date_column)
        elif freq == "monthly":
            return self.monthly_agg(df, date_column)
        else:
            raise DashArgumentException("Unknown date aggregation frequency")

    @chained_cached_command()
    def date_agg(self, df, date_column, freq):
        return self.date_agg_uncached(df, date_column, freq)

    def daily_agg(self, df, columns):
        if not isinstance(columns, list):
            columns = [columns]
        date_column = columns[0]
        """Adds an aggregation by day"""
        df = self.date_manipulations(df, date_column, "daily")
        df = df.groupby(columns)
        return df

    def monthly_agg(self, df, columns):
        """Adds an aggregation by month"""
        if not isinstance(columns, list):
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
        if isinstance(res, pd.core.series.Series):
            res = res.reset_index()

        return res

    @final_cached_command()
    def sum_over_time(self, df, date_column, column, freq):
        df = self.date_manipulations(df, date_column, freq)
        df = df.sort_values(by=date_column, ascending=True)
        df = df.groupby(date_column)[column].sum().to_frame().reset_index()
        df[column] = df[column].cumsum()
        return df

    @final_cached_command()
    def cumsum(self, df, column):
        """Cumulative sum"""
        return df[column].cumsum()

    @chained_cached_command()
    def monthly_sample(self, df, date_column):
        """Samples daily data into monthly data"""
        return df.groupby(pd.DatetimeIndex(df[date_column]).to_period('M')).nth(-1).reset_index(drop=True)

    def date_manipulations(self, df, date_column, freq):
        if date_column not in df:
            raise DashArgumentException(f"Unknown column '{date_column}'")
        if freq == "daily":
            return self.date_manipulations_daily(df, date_column)
        elif freq == "monthly":
            return self.date_manipulations_monthly(df, date_column)

    def date_manipulations_monthly(self, df, date_column):
        df[date_column] = pd.to_datetime(df[date_column]).dt.to_period("M")
        df[date_column] = pd.to_datetime(df[date_column].dt.start_time).dt.date
        return df

    def date_manipulations_daily(self, df, date_column):
        if not (df.empty):
            df[date_column] = (
                df[date_column]
                .dt.tz_localize(None)
                .dt.floor("D")
                .dt.date
            )
        return df
