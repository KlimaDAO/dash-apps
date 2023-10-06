from __future__ import annotations  # noqa
import pandas as pd
import numpy as np
from . import (
    S3,
    helpers,
    DfCacheable,
    chained_cached_command,
    final_cached_command,
)


class Credits(DfCacheable):
    """Service for credits"""
    def __init__(self, commands=[]):
        super(Credits, self).__init__(commands)

    def load_df(self, bridge: str, pool: str, status: str):
        s3 = S3()
        # Offchain data
        if bridge in ["offchain"]:
            if status == "issued":
                df = s3.load("verra_data_v2")
            # This is a hack to get all retired offsets even if the retirements occured offchain
            elif status == "all_retired":
                df = s3.load("verra_data_v2")
                df = df[df["status"] == "Retired"]
            elif status == "retired":
                df = s3.load("verra_retirements")
            else:
                raise helpers.DashArgumentException(f"Unknown credit status {status}")
        # One Bridge data
        elif bridge in ["toucan", "c3", "polygon"]:
            if status == "bridged":
                df = s3.load("polygon_bridged_offsets_v2")
            elif status in ["retired", "all_retired"]:
                df = s3.load("polygon_retired_offsets_v2")
            else:
                raise helpers.DashArgumentException(f"Unknown credit status {status}")
        elif bridge in ["moss", "eth"]:
            if status == "bridged":
                df = s3.load("eth_moss_bridged_offsets_v2")
            elif status in ["retired", "all_retired"]:
                df = s3.load("eth_retired_offsets_v2")
            else:
                raise helpers.DashArgumentException(f"Unknown credit status {status}")
        # All bridges data concatenated
        elif bridge == "all":
            dfs = []
            for bridg in helpers.ALL_BRIDGES:
                bridg_df = self.load_df(bridg, pool, status)
                date_column = helpers.status_date_column(status)
                bridg_df = bridg_df[[
                    "token_address",
                    date_column,
                    "project_id",
                    "project_id_key",
                    "project_type",
                    "region",
                    "country",
                    "country_code",
                    "methodology",
                    "vintage",
                    "name",
                    "quantity"
                ]]
                dfs.append(bridg_df)
            df = pd.concat(dfs)
            # Prevent further filtering
            return df
        else:
            raise helpers.DashArgumentException(f"Unknown bridge {bridge}")

        # Filter bridge
        if bridge in helpers.ALL_BRIDGES:
            df = df[df["bridge"].str.lower() == bridge.lower()].reset_index(drop=True)

        # Filter pool
        if pool and pool != "all":
            quantity_column = f"{pool}_quantity"
            df = df[df[quantity_column] > 0]

        return df

    @chained_cached_command()
    def filter(self, df, bridge, pool, status):
        """Filters credits on bridge pool and status"""
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
        df = df.groupby(["country", "country_code"])
        return df

    @chained_cached_command()
    def projects_agg(self, df):
        df = df.groupby("project_type")
        return df

    @chained_cached_command()
    def methodologies_agg(self, df):
        df = df.groupby("methodology")
        return df

    @chained_cached_command()
    def pool_summary(self, df, date_field):
        columns = [
            "quantity",
            "total_quantity",
            "bct_quantity",
            "nct_quantity",
            "ubo_quantity",
            "nbo_quantity",
            "mco2_quantity"
        ]

        def summary(df):
            res_df = pd.DataFrame()
            res_df[date_field] = [df[date_field].iloc[0]]

            for column in columns:
                if column in df:
                    res_df[column] = [df[column].sum()]
            return res_df

        df = df.apply(summary).reset_index(drop=True)
        return df

    @chained_cached_command()
    def bridge_summary(self, df, kept_fields):
        column = "quantity"
        if not isinstance(kept_fields, list):
            kept_fields = [kept_fields]

        def summary(df):
            res_df = pd.DataFrame()
            for kept_field in kept_fields:
                res_df[kept_field] = [df[kept_field].iloc[0]]
            bridged_quantity = 0
            for bridge in helpers.ALL_BRIDGES:
                filtered_df = df[df["bridge"].str.lower() == bridge.lower()]
                this_bridge_quantity = filtered_df[column].sum()
                res_df[f"{bridge}_quantity"] = [this_bridge_quantity]
                bridged_quantity = bridged_quantity + this_bridge_quantity
            total_quantity = df[column].sum()
            res_df["total_quantity"] = [total_quantity]
            res_df["not_bridged_quantity"] = [total_quantity - bridged_quantity]
            return res_df

        df = df.apply(summary).reset_index(drop=True)
        return df

    @final_cached_command()
    def average(self, df, column, weights):
        if df[weights].sum() == 0:
            return 0
        return np.average(df[column], weights=df[weights])

    def filter_pool_quantity(self, df, quantity_column):
        df = df[df[quantity_column] > 0]
        df["quantity"] = df[quantity_column]
        kept_columns = [
                "project_id",
                "project_id_key",
                "vintage",
                "quantity",
                "region",
                "country",
                "name",
                "project_type",
                "methodology",
                "token_address",
            ]
        for date_field in ["retirement_date", "deposited_date", "redeemed_date", "bridged_date"]:
            if date_field in df:
                kept_columns = kept_columns + [date_field]

        df = df[kept_columns].reset_index(drop=True)

        return df

    def drop_duplicates(self, df):
        df = df.drop_duplicates(subset=["token_address"], keep="first")
        df = df.reset_index(drop=True)
        return df
