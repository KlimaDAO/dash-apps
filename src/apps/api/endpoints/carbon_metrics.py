from flask_restful import Resource
from src.apps.services import Metrics as Service, layout_cache
from . import helpers


class CarbonMetrics(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, bridge):
        service = Service()
        if bridge == "eth":
            metrics = service.eth()
        elif bridge == "polygon":
            metrics = service.polygon()
        elif bridge == "celo":
            metrics = service.celo()
        else:
            raise Exception("Unknown chain")
        return metrics
