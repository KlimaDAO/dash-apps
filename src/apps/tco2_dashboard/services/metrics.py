from . import S3
from . import KeyCacheable, chained_cached_command, final_cached_command


class Metrics(KeyCacheable):
    def __init__(self, commands=[]):
        super(Metrics, self).__init__(commands)

    @chained_cached_command()
    def polygon(self, df):
        """Get polygon carbon metrics"""
        df = S3().load("raw_polygon_carbon_metrics")
        print(df)
        return df

    @chained_cached_command()
    def eth(self, df):
        """Get eth carbon metrics"""
        df = S3().load("raw_eth_carbon_metrics")
        return df

    @chained_cached_command()
    def celo(self, df):
        """Get eth carbon metrics"""
        df = S3().load("raw_celo_carbon_metrics")
        return df

    @final_cached_command()
    def latest(self, df):
        """Returns the latest Metric"""
        return df.iloc[0]
