import pandas as pd
import math
from flask_restful import Resource, reqparse
from src.apps.services import Offsets as Service

MAX_PAGE_SIZE = 20


def validate_page_size(s):
    try:
        s = int(s)
    except ValueError:
        raise Exception("page_size must be an integer")
    if s >= 1 and s <= MAX_PAGE_SIZE:
        return s
    raise Exception(f"page_size must be between 1 and {MAX_PAGE_SIZE}")


def validate_list(valid_values):
    def func(s):
        if s in valid_values:
            return s
        raise Exception(f"Valid values are {', '.join(valid_values)}")
    return func


parser = reqparse.RequestParser()
parser.add_argument('page', type=int, default=0)
parser.add_argument('page_size', type=validate_page_size, default=0)
parser.add_argument('bridge',
                    type=validate_list(["all", "offchain", "Toucan", "C3", "Moss", "Polygon", "Eth"]), default="all")
parser.add_argument('pool', type=validate_list(["UBO", "NBO", "NCT", "BCT", None]), default=None)
parser.add_argument('offset_status',
                    type=validate_list(["issued", "bridged", "deposited", "redeemed", "retired", None]), default=None)


class Offsets(Resource):
    def get(self):
        # Parse arguments
        args = parser.parse_args()
        page = args["page"]
        bridge = args["bridge"]
        pool = args["pool"]
        page_size = args["page_size"]
        offset_status = args["offset_status"]
        if offset_status is None:
            offset_status = "issued" if bridge == "offchain" else "bridged"

        # Fetch and slice data
        df: pd.DataFrame = Service().filter(bridge, pool, offset_status).resolve()
        items_count = df.shape[0]
        df = df[page_size * page:page_size * (page + 1)]
        pages_count = math.ceil(items_count / page_size)

        # Return result
        return {
            "items": df.to_dict('records'),
            "items_count": items_count,
            "current_page": page,
            "pages_count": pages_count
        }
