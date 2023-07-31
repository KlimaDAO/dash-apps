import pandas as pd
from . import S3, KeyCacheable, services_short_cache, single_cached_command


class Prices(KeyCacheable):
    """Service for token prices"""
    def __init__(self, commands=[], cache=services_short_cache):
        super(Prices, self).__init__(commands, cache)

    def build_df(self):
        # Merge regular asset prices with latest asset prices
        latest_prices_df = S3(cache=services_short_cache).load("current_assets_prices")
        print(latest_prices_df["bct_price"])
        df = S3().load("assets_prices")
        # Replace latest entry
        latest_date = latest_prices_df.iloc[0]["date"]
        df.drop(df[df["date"] == latest_date].index, inplace=True)
        df = pd.concat([latest_prices_df, df])

        self.df = df

    @single_cached_command()
    def dataset(self):
        self.build_df()
        return self.df

    @single_cached_command()
    def token(self, token):
        self.build_df()
        col_name = f"{token}_price"
        a = self.df[col_name].isna()
        return self.df[~a].rename(columns={
            col_name: "price"
        })
