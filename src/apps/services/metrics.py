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
        all["total_retirements"] = (
            all["total_retirements_polygon"] +
            all["total_retirements_eth"] +
            all["total_retirements_celo"]
        )
        all = all.drop(columns=[
            "date_eth",
            "date_celo",
            "date_polygon"
        ])
        all = all.fillna(method="backfill")
        all = all.fillna(0)

        # Compute cross chain protocol data
        all["total_nct_supply"] = all.nct_supply_polygon + all.nct_supply_celo
        all["total_bct_supply"] = all.bct_supply_polygon + all.bct_supply_celo
        all["total_nbo_supply"] = all.nbo_supply_polygon
        all["total_ubo_supply"] = all.ubo_supply_polygon
        all["total_mco2_supply"] = all.mco2_supply_polygon + all.mco2_supply_celo + all.mco2_supply_eth

        all["total_toucan_supply"] = all.total_bct_supply + all.total_nct_supply
        all["total_c3_supply"] = all.total_ubo_supply + all.total_nbo_supply
        all["total_moss_supply"] = all.total_mco2_supply

        return all

    @final_cached_command()
    def latest(self, df):
        """Returns the latest Metric"""
        return df.iloc[0]

    @final_cached_command()
    def days_ago(self, df, days_ago):
        """Returns the Metric from days_ago"""
        return df.iloc[days_ago - 1]
