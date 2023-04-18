from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types  \
    import ChartContent, ListData, TopContent


class RetirementTrendsInterface:

    def create_header(self) -> str:
        """Return header data for a particular retirement trend"""
        pass

    def create_top_content(self) -> TopContent:
        """Return all necessary data required
        for the top part for a page of a particular retirement trend"""
        pass

    def create_chart_content(self) -> ChartContent:
        """Return all necessary data required
        for the chart part for a page of a particular retirement trend"""

        pass

    def create_list_data(self) -> ListData:
        """Return all necessary data required
        for the list part for a page of a particular retirement trend"""

        pass
