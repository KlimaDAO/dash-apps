from flask_restful import Resource
from src.apps.services import Metrics as Service, layout_cache, DashArgumentException
from . import helpers


class CarbonMetrics(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, chain):
        service = Service()
        if chain == "eth":
            metrics = service.eth()
        elif chain == "polygon":
            metrics = service.polygon()
        elif chain == "celo":
            metrics = service.celo()
        else:
            raise DashArgumentException(f"Unknown chain '{chain}'")
        return metrics
