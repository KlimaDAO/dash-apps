from . import S3, DfCacheable, chained_cached_command, final_cached_command


class Metrics(DfCacheable):
    """Service for carbon metrics"""
    def __init__(self, commands=[]):
        super(Metrics, self).__init__(commands)

    @chained_cached_command()
    def polygon(self, _df):
        """Get polygon carbon metrics"""
        return S3().load("polygon_carbon_metrics")

    @chained_cached_command()
    def eth(self, _df):
        """Get eth carbon metrics"""
        return S3().load("eth_carbon_metrics")

    @chained_cached_command()
    def celo(self, _df):
        """Get eth carbon metrics"""
        return S3().load("celo_carbon_metrics")

    @chained_cached_command()
    def all(self, _df):
        """Get merged carbon metrics"""
        celo = S3().load("celo_carbon_metrics").add_suffix("_celo")
        eth = S3().load("eth_carbon_metrics").add_suffix("_eth")
        polygon = S3().load("polygon_carbon_metrics").add_suffix("_polygon")

        all = polygon
        all = all.merge(eth, how="outer", left_on="date_polygon", right_on="date_eth")
        all = all.merge(celo, how="outer", left_on="date_polygon", right_on="date_celo")
        all["date"] = all.date_polygon.combine_first(all.date_eth).combine_first(all.date_celo)
        all = all.rename(columns={
            "total_klima_retirements_polygon": "total_klima_retirements",
            "date_polygon": "date"
        })
        all["total_retirements"] = (
            all["total_retirements_polygon"] +
            all["total_retirements_eth"] +
            all["total_retirements_celo"]
        )
        all = all.drop(columns=[
            "date_eth",
            "date_celo",
            "total_retirements_polygon",
            "total_retirements_eth",
            "total_retirements_celo"
        ])
        all = all.fillna(0)
        return all

    @final_cached_command()
    def latest(self, df):
        """Returns the latest Metric"""
        return df.iloc[0]

    @final_cached_command()
    def days_ago(self, df, days_ago):
        """Returns the Metric from days_ago"""
        return df.iloc[days_ago - 1]
