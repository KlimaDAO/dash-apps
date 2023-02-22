TYPE_TOKEN = "TOKEN"
TYPE_POOL = "POOL"
TYPE_CHAIN = "CHAIN"


class RetirementTrendInputs:

    def __init__(
            self,
            df_carbon_metrics_polygon,
            df_carbon_metrics_eth,
            raw_klima_retirements_df,
            daily_agg_klima_retirements_df,
            df_verra_retired,
            df_verra,
            bridges_info_dict,
            verra_fallback_note):

        self.df_carbon_metrics_polygon = df_carbon_metrics_polygon
        self.df_carbon_metrics_eth = df_carbon_metrics_eth
        self.raw_klima_retirements_df = raw_klima_retirements_df
        self.daily_agg_klima_retirements_df = daily_agg_klima_retirements_df
        self.df_verra_retired = df_verra_retired
        self.df_verra = df_verra
        self.bridges_info_dict = bridges_info_dict
        self.verra_fallback_note = verra_fallback_note


class TopContent:

    def __init__(
            self,
            data):

        self.data = data


class ChartData:

    def __init__(
            self,
            header,
            figure):

        self.header = header
        self.figure = figure


class ListData:

    def __init__(
            self,
            dataframe):

        self.dataframe = dataframe
