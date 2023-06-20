from . import S3
from . import KeyCacheable, chained_cached_command, final_cached_command


class Metrics(KeyCacheable):
    """Service for carbon metrics"""
    def __init__(self, commands=[]):
        super(Metrics, self).__init__(commands)

    @chained_cached_command()
    def polygon(self, _df):
        """Get polygon carbon metrics"""
        return S3().load("raw_polygon_carbon_metrics")

    @chained_cached_command()
    def eth(self, _df):
        """Get eth carbon metrics"""
        return S3().load("raw_eth_carbon_metrics")

    @chained_cached_command()
    def celo(self, _df):
        """Get eth carbon metrics"""
        return S3().load("raw_celo_carbon_metrics")

    @final_cached_command()
    def latest(self, df):
        """Returns the latest Metric"""
        return df.iloc[0]

    @final_cached_command()
    def days_ago(self, df, days_ago):
        """Returns the Metric from days_ago"""
        return df.iloc[days_ago - 1]
