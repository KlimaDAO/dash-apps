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
        # autoselect bridge
        if status == "retired":
            df = s3.load("polygon_pools_retired_offsets")
        elif status == "deposited":
            df = s3.load("polygon_pools_deposited_offsets")
        elif status == "redeemed":
            df = s3.load("polygon_pools_redeemed_offsets")
        else:
            raise helpers.DashArgumentException(f"Unknown credit status {status}")

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

    def filter_df_by_pool(self, df, pool):
        pool_address = Tokens().get(pool)["address"]
        df = df[(df["pool"] == pool_address)].reset_index(drop=True)
        return df
