from flask_restful import Resource, reqparse
from src.apps.services import Offsets as Service
from . import helpers


def validate_list(valid_values):
    def func(s):
        if s in valid_values:
            return s
        raise Exception(f"Valid values are {', '.join(valid_values)}")
    return func


BRIDGES = ["all", "offchain", "Toucan", "C3", "Moss", "Polygon", "Eth"]
POOLS = ["UBO", "NBO", "NCT", "BCT"]
STATUSES = ["issued", "bridged", "deposited", "redeemed", "retired"]

parser = reqparse.RequestParser()
parser.add_argument('bridge', type=validate_list(BRIDGES), default="all")
parser.add_argument('pool', type=validate_list(POOLS + [None]), default=None)
parser.add_argument('offset_status', type=validate_list(STATUSES + [None]), default=None)


class Offsets(Resource):
    @helpers.with_help(
        f"""Query Parameters
        bridge: one of {BRIDGES}
        pool: one of {POOLS}
        offset_status: one of {STATUSES}
        {helpers.PAGINATION_HELP}
        """
    )
    @helpers.with_pagination
    def get(self):
        # Parse arguments
        args = parser.parse_args()
        bridge = args["bridge"]
        pool = args["pool"]
        offset_status = args["offset_status"]
        if offset_status is None:
            offset_status = "issued" if bridge == "offchain" else "bridged"

        # Fetch and slice data
        return Service().filter(bridge, pool, offset_status).resolve()
