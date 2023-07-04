from __future__ import annotations
import pandas as pd
import numpy as np
from . import S3, Countries, Tokens, constants, KeyCacheable, chained_cached_command, final_cached_command


class Offsets(KeyCacheable):
    """Service for offsets"""
    def __init__(self, commands=[]):
        super(Offsets, self).__init__(commands)

    def load_df(self, bridge, pool, status):
        is_pool_df = False
        s3 = S3()
        # Offchain data
        if bridge in ["offchain"]:
            df = s3.load("verra_data_v2")
            if status == "issued":
                pass
            elif status == "retired":
                df = self.verra_retired(df)
            else:
                raise Exception(f"Unknown offset status {status}")
        # One Bridge data
        elif bridge in ["Toucan", "C3", "Polygon"]:
            if status == "bridged":
                df = s3.load("polygon_bridged_offsets_v2")
            elif status == "retired":
                if pool is None:
                    df = s3.load("polygon_retired_offsets_v2")
                else:
                    df = s3.load("polygon_pools_retired_offsets")
                    is_pool_df = True
            elif status == "deposited":
                df = s3.load("polygon_pools_deposited_offsets")
                is_pool_df = True
            elif status == "redeemed":
                df = s3.load("polygon_pools_redeemed_offsets")
                is_pool_df = True
            else:
                raise Exception(f"Unknown offset status {status}")
        elif bridge in ["Moss", "Eth"]:
            if status == "bridged":
                df = s3.load("eth_moss_bridged_offsets_v2")
            elif status == "retired":
                df = s3.load("eth_retired_offsets_v2")
            else:
                raise Exception(f"Unknown offset status {status}")
        # All bridges data concatenated
        elif bridge == "all":
            dfs = []
            for bridg in constants.ALL_BRIDGES:
                bridg_df = self.load_df(bridg, pool, status)
                date_column = Offsets.status_date_column(status)
                bridg_df = bridg_df[[date_column, "Quantity", "Bridge"]]
                dfs.append(bridg_df)

            df = pd.concat(dfs)
        else:
            raise Exception(f"Unknown bridge {bridge}")

        # Filter bridge
        if not is_pool_df:
            if bridge in constants.ALL_BRIDGES:
                df = df[df["Bridge"] == bridge].reset_index()

        # Filter pool
        if pool:
            if not is_pool_df:
                df = self.drop_duplicates(df)
                if pool == "all":
                    df = self.filter_pool_quantity(df, "Total Quantity")
                else:
                    df = self.filter_pool_quantity(df, f"{pool} Quantity")
            elif pool != "all":
                df = self.filter_df_by_pool(df, pool)

        return df

    @chained_cached_command()
    def filter(self, df, bridge, pool, status):
        """Filters offsets on bridge pool and status"""
        # Load dataset
        df = self.load_df(bridge, pool, status)
        return df

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

    @chained_cached_command()
    def daily_agg(self, df, date_column):
        """Adds an aggregation by day"""
        df = self.date_manipulations(df, date_column, "daily")
        df = df.groupby(date_column)
        return df

    @chained_cached_command()
    def monthly_agg(self, df, date_column):
        """Adds an aggregation by day"""
        df = self.date_manipulations(df, date_column, "monthly")
        df = df.groupby(date_column)
        return df

    @chained_cached_command()
    def vintage_agg(self, df):
        """Adds an aggregation on vintage"""
        df = df.groupby("Vintage")
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
    def project_agg(self, df):
        df = df.groupby("Project Type")
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

    def _summary(self, df, result_cols):
        """Creates a summary"""
        group_by_cols = result_cols.copy()
        group_by_cols.remove("Quantity")
        df = (
            df.groupby(group_by_cols)["Quantity"]
            .sum()
            .to_frame()
            .reset_index()
        )
        df = df[result_cols]
        return df

    @final_cached_command()
    def pool_summary(self, df):
        """Creates a summary for pool data"""
        return self._summary(df, [
            "Project ID",
            "Token Address",
            "View on PolygonScan",
            "Quantity",
            "Vintage",
            "Country",
            "Project Type",
            "Methodology",
            "Name"
         ])

    @final_cached_command()
    def bridge_summary(self, df):
        """Creates a summary for bridge data"""
        return self._summary(df, [
            "Project ID",
            "Quantity",
            "Vintage",
            "Country",
            "Project Type",
            "Methodology",
            "Name"
        ])

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

    @final_cached_command()
    def average(self, df, column, weights):
        if df[weights].sum() == 0:
            return 0
        return np.average(df[column], weights=df[weights])

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

    def filter_df_by_pool(self, df, pool):
        pool_address = Tokens().get(pool)["address"]
        df["Pool"] = df["Pool"].str.lower()
        df = df[(df["Pool"] == pool_address)].reset_index()
        return df

    def drop_duplicates(self, df):
        df = df.drop_duplicates(subset=["Token Address"], keep="first")
        df = df.reset_index(drop=True)
        return df

    def verra_retired(self, df):
        df = df.query("~Toucan & ~C3 & ~Moss")
        df = df[df["Status"] == "Retired"]
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def status_date_column(status):
        if status == "issued":
            return "Issuance Date"
        elif status == "bridged":
            return "Bridged Date"
        elif status == "retired":
            return "Retirement Date"
        elif status == "redeemed":
            return "Redeemed Date"
        elif status == "deposited":
            return "Deposited Date"
        else:
            raise Exception("Unknown status")
