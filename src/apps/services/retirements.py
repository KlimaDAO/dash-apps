import pandas as pd
from . import (
    S3,
    DashArgumentException,
    DfCacheable,
    final_cached_command,
    chained_cached_command,
    single_cached_command,
    helpers
)


def summary(df):
    res_df = pd.DataFrame()
    res_df["retirement_date"] = [df["retirement_date"].iloc[0]]
    res_df["amount_retired"] = [df["quantity"].sum()]
    res_df["number_of_retirements"] = [df["quantity"].count()]
    for token in helpers.ALL_TOKENS:
        filtered_df = df[df["token"] == token.upper()]
        res_df[f"amount_retired_{token}"] = [filtered_df["quantity"].sum()]
        res_df[f"number_of_retirements_{token}"] = [filtered_df["quantity"].count()]
    return res_df


class Retirements(DfCacheable):
    """Service for carbon metrics"""
    def __init__(self, commands=[]):
        super(Retirements, self).__init__(commands)

    def getDf(self, filter):
        """Get klima retirements"""
        if filter == "all":
            return S3().load("all_retirements")
        elif filter == "klima":
            return S3().load("polygon_klima_retirements")
        else:
            raise DashArgumentException(f"Unknown retirements filter {filter}")

    @single_cached_command()
    def raw(self, filter):
        """Get klima retirements"""
        return self.getDf(filter)

    @chained_cached_command()
    def get(self, _df, filter):
        """Get klima retirements"""
        return self.getDf(filter)

    @final_cached_command()
    def filter_tokens(self, df, tokens):
        """Filter klima retirements on tokens"""
        if df is None:
            df = S3().load("polygon_klima_retirements")

        return df[
            df['token'].isin(tokens)
        ]

    @chained_cached_command()
    def summary(self, df):
        df = df.apply(summary).reset_index(drop=True)
        return df

    @chained_cached_command()
    def beneficiaries_agg(self, df):
        df = df.groupby("beneficiary")
        return df

    @chained_cached_command()
    def tokens_agg(self, df):
        df = df.groupby("token")
        return df
