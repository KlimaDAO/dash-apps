import pandas as pd
from . import S3, DfCacheable, services_short_cache, chained_cached_command


class Prices(DfCacheable):
    """Service for token prices"""
    def __init__(self, commands=[], cache=services_short_cache):
        super(Prices, self).__init__(commands, cache)

    def load_df(self):
        # Merge regular asset prices with latest asset prices
        latest_prices_df = S3(cache=services_short_cache).load("current_assets_prices")
        df = S3().load("assets_prices")
        # Replace latest entry
        latest_date = latest_prices_df.iloc[0]["date"]
        df.drop(df[df["date"] == latest_date].index, inplace=True)
        df = pd.concat([latest_prices_df, df])

        return df

    @chained_cached_command()
    def filter(self, df_, token):
        df = self.load_df()
        if token:
            price_col_name = f"{token}_price"
            address_col_name = f"{token}_address"
            a = df[price_col_name].isna()
            df = df[~a].rename(columns={
                price_col_name: "price",
                address_col_name: "address",
            })
            df = df[["date", "address", "price"]]
        return df
