from . import S3, DfCacheable, final_cached_command, chained_cached_command, single_cached_command


class KlimaRetirements(DfCacheable):
    """Service for carbon metrics"""
    def __init__(self, commands=[]):
        super(KlimaRetirements, self).__init__(commands)

    def getDf(self):
        """Get klima retirements"""
        return S3().load("polygon_klima_retirements")

    @single_cached_command()
    def raw(self):
        """Get klima retirements"""
        return self.getDf()

    @chained_cached_command()
    def get(self, _df):
        """Get klima retirements"""
        return self.getDf()

    @final_cached_command()
    def filter_tokens(self, df, tokens):
        """Filter klima retirements on tokens"""
        if df is None:
            df = S3().load("raw_polygon_klima_retirements")

        return df[
            df['dailyKlimaRetirements_token'].isin(tokens)
        ]

    @chained_cached_command()
    def beneficiaries_agg(self, df):
        df = df.groupby("Beneficiary Address")
        return df
