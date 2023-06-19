import pandas as pd
import numpy as np
from . import S3
from . import Countries
from . import KeyCacheable, chained_cached_command, final_cached_command


class Offsets(KeyCacheable):
    def __init__(self, commands=[]):
        super(Offsets, self).__init__(commands)

    @chained_cached_command()
    def filter(self, df, bridge, status):
        """Adds a bridge filter"""
        s3 = S3()
        if status == "bridged":
            df = s3.load("polygon_bridged_offsets")
        else:
            df = s3.load("polygon_retired_offsets")

        # TODO: Maybe this should be done in the data pipelines
        if not (df.empty):
            if "Vintage" in df.columns:
                df["Vintage Year"] = (
                    pd.to_datetime(df["Vintage"], unit="s").dt.tz_localize(None).dt.year
                )

        return df[df["Bridge"] == bridge].reset_index()

    @chained_cached_command()
    def date_range(self, df, begin, end):
        """Adds a date range filter"""
        if type(end) != int:
            end = end.timestamp()
        if type(begin) != int:
            begin = begin.timestamp()
        df = df[
            (df["Date"] <= end)
            & (df["Date"] > begin)
        ]
        return df

    @chained_cached_command()
    def daily_agg(self, df):
        """Adds an aggregation by day"""
        df = self.date_manipulations(df)
        df = df.groupby("Date")
        return df

    @chained_cached_command()
    def vintage_agg(self, df):
        """Adds an aggregation on vintage"""
        df = df.groupby("Vintage Year")
        return df

    @chained_cached_command()
    def country_agg(self, df):
        df["Country Code"] = [
            Countries().get_country(country) for country in df["Country"]
        ]
        df["Country Text"] = df["Country Code"].astype(str)
        df = df.groupby(["Country", "Country Text", "Country Code"])
        return df

    @chained_cached_command()
    def methodology_agg(self, df):
        df = df.groupby("Methodology")
        return df

    @final_cached_command()
    def sum(self, df, column):
        """Sums results, works also on aggregations"""
        res = df[column].sum()

        # Reset index if we are computing aggregated sums
        if type(res) == pd.core.series.Series:
            res = res.reset_index()

        return res

    @final_cached_command()
    def average(self, df, column, weights):
        if df[weights].sum() == 0:
            return 0
        return np.average(df[column], weights=df[weights])

    def date_manipulations(self, df):
        # TODO: Dates shall be already manipulated at data pipelines level
        if not (df.empty):
            df["Date"] = (
                pd.to_datetime(df["Date"], unit="s")
                .dt.tz_localize(None)
                .dt.floor("D")
                .dt.date
            )
            datelist = pd.date_range(
                start=df["Date"].min() + pd.DateOffset(-1),
                end=pd.to_datetime("today"),
                freq="d",
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
                df_date, how="right", left_on="Date", right_on="Date_continous"
            ).reset_index(drop=True)
            df["Date"] = df["Date_continous"]
            for i in df.columns:
                if "Quantity" in i:
                    df[i] = df[i].fillna(0)
                else:
                    df[i] = df[i].fillna("missing")
                    df[i] = df[i].replace("", "missing")
        return df
