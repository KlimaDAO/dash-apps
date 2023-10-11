from flask_restful import Resource, reqparse
from src.apps.services import Credits as Service, layout_cache
from . import helpers


BRIDGES = ["all", "offchain", "toucan", "c3", "moss", "polygon", "eth"]
POOLS = ["ubo", "nbo", "nct", "bct", "all"]
STATUSES = ["issued", "bridged", "deposited", "redeemed", "retired", "all_retired", "all"]
OFFCHAIN_FILTER = ["tokenized", "toucan", "c3", "moss"]
DATE_FIELDS = [
    "bridged_date",
    "issuance_date",
    "retirement_date",
]
BASE_HELP = f"""Query Parameters
        bridge: one of {BRIDGES}
        pool: one of {POOLS}
        status: one of {STATUSES}
        """

credits_filter_parser = reqparse.RequestParser()
credits_filter_parser.add_argument('bridge', type=helpers.validate_list(BRIDGES), default="all")
credits_filter_parser.add_argument('pool', type=helpers.validate_list(POOLS + [None]), default=None)
credits_filter_parser.add_argument('status', type=helpers.validate_list(STATUSES + [None]), default=None)
credits_filter_parser.add_argument(
    'offchain_filter',
    type=helpers.validate_list(OFFCHAIN_FILTER + [None]),
    default=None
)


class AbstractCredits(Resource):

    def get_default_date_field(self):
        # returns the date field appropriate given the selected status
        args = credits_filter_parser.parse_args()
        bridge = args["bridge"]
        status = args["status"]

        if status is None:
            return "issuance_date" if bridge == "offchain" else "bridged_date"
        else:
            return helpers.status_date_column(status)

    @helpers.with_daterange_filter("bridged_date")
    @helpers.with_daterange_filter("issuance_date")
    @helpers.with_daterange_filter("retirement_date")
    @helpers.with_daterange_filter("deposited_date")
    @helpers.with_daterange_filter("redeemed_date")
    def get_credits(self, bridge=None):
        args = credits_filter_parser.parse_args()
        if not bridge:
            bridge = args["bridge"]
        pool = args["pool"]
        status = args["status"]
        offchain_filter = args["offchain_filter"]

        # Accept a 'all' value for pools
        if pool == "all":
            pool = None

        # Accept a 'all' value for status
        if status == "all":
            status = None

        # auto select status
        if status is None:
            status = "issued" if bridge == "offchain" else "bridged"

        # Select credits
        df = Service().filter(bridge, pool, status)

        # Filter offchain credits
        if offchain_filter:
            df = df.offchain_filter(offchain_filter)

        return df

    def get_pool_credits(self, bridge=None):
        return self.get_credits(bridge).pool_analysis()


class CreditsRaw(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        return self.get_credits()


class CreditsDatesAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.dates_aggregation_help(DATE_FIELDS)}
        {helpers.OUTPUT_FORMATTER_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, freq):
        return helpers.apply_date_aggregation(
            DATE_FIELDS,
            self.get_credits(),
            freq,
            self.get_default_date_field()
        )


class CreditsCountriesAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        credits = self.get_credits().countries_agg().sum("quantity")
        return credits


class CreditsProjectsAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        credits = self.get_credits().projects_agg().sum("quantity")
        return credits


class CreditsMethodologiesAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        credits = self.get_credits().methodologies_agg().sum("quantity")
        return credits


class CreditsVintageAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        credits = self.get_credits().vintage_agg().sum("quantity")
        return credits


class CreditsPoolVintageAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        credits = self.get_pool_credits().vintage_agg().pool_summary("vintage")
        return credits


class CreditsPoolAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        """
    )
    def get(self):
        credits = self.get_pool_credits().pool_summary().resolve().to_dict(orient='records')[0]
        return credits


class CreditsPoolMethodologyAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        credits = self.get_pool_credits().methodologies_agg().pool_summary("methodology")
        return credits


class CreditsPoolDatesAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, freq):
        date_column = self.get_default_date_field()
        credits = self.get_pool_credits().date_agg(date_column, freq).pool_summary(date_column)
        return credits


class CreditsBridgeVintageAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        credits = self.get_credits(bridge="offchain").vintage_agg().bridge_summary("vintage")
        return credits


class CreditsBridgeCountriesAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        credits = self.get_credits(bridge="offchain").countries_agg().bridge_summary(["country_code", "country"])
        return credits


class CreditsBridgeDateAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.dates_aggregation_help(DATE_FIELDS)}
        {helpers.OUTPUT_FORMATTER_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, freq):
        return self.get_credits(bridge="offchain").date_agg("issuance_date", freq).bridge_summary("issuance_date")


class CreditsBridgeAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.dates_aggregation_help(DATE_FIELDS)}
        {helpers.DATES_FILTER_HELP}
        """
    )
    def get(self):
        return self.get_credits(bridge="offchain").bridge_summary("quantity").resolve().to_dict(orient='records')[0]


class CreditsGlobalAggregation(AbstractCredits):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        """
    )
    def get(self):
        return {
            "quantity": self.get_credits().sum("quantity")
        }
