import pandas as pd
from . import (
    helpers,
    S3,
    Tokens,
    Credits,
    DfCacheable,
    DashArgumentException,
    chained_cached_command,
    final_cached_command
)


class Pools(DfCacheable):
    """Service for pools"""
    def __init__(self, commands=[]):
        super(Pools, self).__init__(commands)

    def load_df(self, pool, status):
        s3 = S3()
        if status == "retired":
            df = s3.load("polygon_pools_retired_offsets")
        elif status == "deposited":
            df = s3.load("polygon_pools_deposited_offsets")
        elif status == "redeemed":
            df = s3.load("polygon_pools_redeemed_offsets")
        else:
            raise helpers.DashArgumentException(f"Unknown credit status {status}")
        print(df)
        print(df.columns)
        if pool and pool != "all":
            df = self.filter_df_by_pool(df, pool)

        return df

    @chained_cached_command()
    def filter(self, _df, pool, status) -> str:
        return self.load_df(pool, status)

    @final_cached_command()
    def quantities(self, bridge) -> dict:
        """Returns current pool quantities"""
        bridge = bridge.lower()
        if bridge == "toucan":
            pool_labels = ["BCT", "NCT"]
        elif bridge == "c3":
            pool_labels = ["UBO", "NBO"]
        else:
            raise DashArgumentException("Unknown bridge")
        values = [self.load_df(pool, "deposited").sum("Quantity") for pool in pool_labels]

        pool_labels = pool_labels + ["not_pooled"]
        not_pool_qty = Credits().filter(bridge, "all", "bridged").sum("Quantity") - sum(values)
        values = values + [not_pool_qty]

        return dict(zip(pool_labels, values))

    @chained_cached_command()
    def pool_summary(self, df, date_field):
        tokens = Tokens().get_dict()

        def summary(df):
            res_df = pd.DataFrame()
            res_df[date_field] = [df[date_field].iloc[0]]
            for token in tokens:
                address = tokens[token]["token_address"]
                filtered_df = df[df["pool"] == address]
                res_df[f"{token.lower()}_quantity"] = [filtered_df["quantity"].sum()]
                res_df[f"{token.lower()}_count"] = [filtered_df["quantity"].count()]
            return res_df

        df = df.apply(summary).reset_index(drop=True)
        return df

    def filter_df_by_pool(self, df, pool):
        pool_address = Tokens().get(pool)["token_address"]
        df = df[(df["pool"] == pool_address)].reset_index(drop=True)
        return df
