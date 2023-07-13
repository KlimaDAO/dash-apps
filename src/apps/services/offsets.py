from __future__ import annotations  # noqa
import pandas as pd
import numpy as np
from . import (
    S3,
    Countries,
    Tokens,
    helpers,
    DfCacheable,
    chained_cached_command,
    final_cached_command,
)


class Offsets(DfCacheable):
    """Service for offsets"""
    def __init__(self, commands=[]):
        super(Offsets, self).__init__(commands)

    def load_df(self, bridge: str, pool: str, status: str):
        is_pool_df = False
        s3 = S3()
        # Offchain data
        if bridge in ["offchain"]:
            if status == "issued":
                df = s3.load("verra_data_v2")
            elif status == "retired":
                df = s3.load("verra_retirements")
            else:
                raise helpers.DashArgumentException(f"Unknown offset status {status}")
        # One Bridge data
        elif bridge in ["toucan", "c3", "polygon"]:
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
                raise helpers.DashArgumentException(f"Unknown offset status {status}")
        elif bridge in ["moss", "eth"]:
            if status == "bridged":
                df = s3.load("eth_moss_bridged_offsets_v2")
            elif status == "retired":
                df = s3.load("eth_retired_offsets_v2")
            else:
                raise helpers.DashArgumentException(f"Unknown offset status {status}")
        # All bridges data concatenated
        elif bridge == "all":
            dfs = []
            for bridg in helpers.ALL_BRIDGES:
                bridg_df = self.load_df(bridg, pool, status)
                date_column = Offsets.status_date_column(status)
                bridg_df = bridg_df[[
                    "token_address",
                    date_column,
                    "bridge",
                    "project_id",
                    "project_id_key",
                    "project_type",
                    "region",
                    "country",
                    "methodology",
                    "vintage",
                    "name",
                ]]
                dfs.append(bridg_df)

            df = pd.concat(dfs)
        else:
            raise helpers.DashArgumentException(f"Unknown bridge {bridge}")

        # Filter bridge
        if not is_pool_df:
            if bridge in helpers.ALL_BRIDGES:
                df = df[df["bridge"].str.lower() == bridge.lower()].reset_index(drop=True)

        # Filter pool
        if pool:
            if not is_pool_df:
                df = self.drop_duplicates(df)
                if pool == "all":
                    df = self.filter_pool_quantity(df, "total_quantity")
                else:
                    df = self.filter_pool_quantity(df, f"{pool}_quantity")
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
    def vintage_agg(self, df):
        """Adds an aggregation on vintage"""
        df = df.groupby("vintage")
        return df

    @chained_cached_command()
    def countries_agg(self, df):
        df["country_code"] = [
            Countries().get_country(country) for country in df["country"]
        ]
        df["country_text"] = df["country_code"].astype(str)
        df = df.groupby(["country", "country_text", "country_code"])
        return df

    @chained_cached_command()
    def projects_agg(self, df):
        df = df.groupby("project_type")
        return df

    @chained_cached_command()
    def methodologies_agg(self, df):
        df = df.groupby("methodology")
        return df

    def _summary(self, df, result_cols):
        """Creates a summary"""
        group_by_cols = result_cols.copy()
        group_by_cols.remove("quantity")
        df = (
            df.groupby(group_by_cols)["quantity"]
            .sum()
            .to_frame()
            .reset_index(drop=True)
        )
        df = df[result_cols]
        return df

    @final_cached_command()
    def pool_summary(self, df):
        """Creates a summary for pool data"""
        return self._summary(df, [
            "project_id",
            "token Address",
            "quantity",
            "vintage",
            "country",
            "project_type",
            "methodology",
            "name"
         ])

    @final_cached_command()
    def bridge_summary(self, df):
        """Creates a summary for bridge data"""
        return self._summary(df, [
            "project_id",
            "quantity",
            "vintage",
            "country",
            "project_type",
            "methodology",
            "name"
        ])

    @final_cached_command()
    def average(self, df, column, weights):
        if df[weights].sum() == 0:
            return 0
        return np.average(df[column], weights=df[weights])

    def filter_pool_quantity(self, df, quantity_column):
        filtered = df[df[quantity_column] > 0]
        filtered["quantity"] = filtered[quantity_column]
        filtered = filtered[
            [
                "project_id",
                "vintage",
                "quantity",
                "country",
                "name",
                "project_type",
                "methodology",
                "token_address",
            ]
        ]
        pat = r"VCS-(?P<id>\d+)"
        repl = (
            lambda m: f"https://registry.verra.org/app/projectDetail/VCS/{m.group('id')}"
        )
        filtered["project_url"] = filtered["project_id"].str.replace(pat, repl, regex=True)
        filtered = filtered[
            [
                "project_id",
                "project_url",
                "token_address",
                "quantity",
                "vintage",
                "country",
                "project_type",
                "methodology",
                "name",
            ]
        ].reset_index(drop=True)
        return filtered

    def filter_df_by_pool(self, df, pool):
        pool_address = Tokens().get(pool)["address"]
        df["pool"] = df["pool"].str.lower()
        df = df[(df["pool"] == pool_address)].reset_index(drop=True)
        return df

    def drop_duplicates(self, df):
        df = df.drop_duplicates(subset=["token_address"], keep="first")
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def status_date_column(status):
        if status == "issued":
            return "issuance_date"
        elif status == "bridged":
            return "bridged_date"
        elif status == "retired":
            return "retirement_date"
        elif status == "redeemed":
            return "redeemed_date"
        elif status == "deposited":
            return "deposited_date"
        else:
            raise helpers.DashArgumentException("Unknown status")
