from . import S3, DfCacheable, final_cached_command, chained_cached_command, single_cached_command


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
            raise Exception(f"Unknown retirements filter {filter}")

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
            df['dailyKlimaRetirements_token'].isin(tokens)
        ]

    @chained_cached_command()
    def beneficiaries_agg(self, df):
        df = df.groupby("Beneficiary")
        return df
