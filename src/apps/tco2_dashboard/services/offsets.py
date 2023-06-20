import pandas as pd
import numpy as np
from . import S3
from . import Countries
from . import KeyCacheable, chained_cached_command, final_cached_command


class Offsets(KeyCacheable):
    """Service for offsets"""
    def __init__(self, commands=[]):
        super(Offsets, self).__init__(commands)

    @chained_cached_command()
    def filter(self, df, bridge, pool, status):
        """Filters offsets on bridge pool and status"""
        # Load dataset
        s3 = S3()
        if bridge in ["Toucan", "C3"]:
            if status == "bridged":
                df = s3.load("polygon_bridged_offsets")
            elif status == "retired":
                if pool is None:
                    df = s3.load("polygon_retired_offsets")
                else:
                    df = s3.load("raw_polygon_pools_retired_offsets")
            elif status == "deposited":
                df = s3.load("raw_polygon_pools_deposited_offsets")
            elif status == "redeemed":
                df = s3.load("raw_polygon_pools_redeemed_offsets")
            else:
                raise Exception("Unknown offset status")
        elif bridge in ["Moss"]:
            if status == "bridged":
                df = s3.load("eth_moss_bridged_offsets")
            elif status == "retired":
                df = s3.load("eth_retired_offsets")
            else:
                raise Exception("Unknown offset status")
        else:
            raise Exception("Unknown bridge")
        df = df[df["Bridge"] == bridge].reset_index()

        # Filter pool
        if pool:
            df = self.drop_duplicates(df)
            if pool == "all":
                df = self.filter_pool_quantity(df, "Total Quantity")
            else:
                df = self.filter_pool_quantity(df, f"{pool} Quantity")

        # TODO: Maybe this should be done in the data pipelines
        if "Vintage" in df.columns:
            df["Vintage Year"] = (
                pd.to_datetime(df["Vintage"], unit="s").dt.tz_localize(None).dt.year
            )
        return df

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
    def sum_over_time(self, df, column):
        df[column] = df[column].cumsum()
        df = df.sort_values(by="Date", ascending=True)
        return df

    @final_cached_command()
    def cumsum(self, df, column):
        """Cumulative sum"""
        return df[column].cumsum()

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

    def filter_pool_quantity(self, df, quantity_column):
        filtered = df[df[quantity_column] > 0]
        filtered["Quantity"] = filtered[quantity_column]
        filtered = filtered[
            [
                "Project ID",
                "Vintage",
                "Quantity",
                "Country",
                "Name",
                "Project Type",
                "Methodology",
                "Token Address",
            ]
        ]
        pat = r"VCS-(?P<id>\d+)"
        repl = (
            lambda m: "[VCS-"
            + m.group("id")
            + "](https://registry.verra.org/app/projectDetail/VCS/"
            + m.group("id")
            + ")"
        )
        filtered["Project ID"] = filtered["Project ID"].str.replace(pat, repl, regex=True)
        filtered["View on PolygonScan"] = (
            "["
            + "Click Here"
            + "](https://polygonscan.com/address/"
            + filtered["Token Address"]
            + ")"
        )
        filtered = filtered[
            [
                "Project ID",
                "Token Address",
                "View on PolygonScan",
                "Quantity",
                "Vintage",
                "Country",
                "Project Type",
                "Methodology",
                "Name",
            ]
        ].reset_index(drop=True)
        return filtered

    def filter_df_by_pool(df, pool_address):
        df["Pool"] = df["Pool"].str.lower()
        df = df[(df["Pool"] == pool_address)].reset_index()
        return df

    def drop_duplicates(self, df):
        df = df.drop_duplicates(subset=["Token Address"], keep="first")
        df = df.reset_index(drop=True)
        return df
