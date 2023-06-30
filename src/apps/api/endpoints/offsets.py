import pandas as pd
import math
from flask_restful import Resource
from src.apps.services import Offsets as Service

PAGE_SIZE = 20


class Offsets(Resource):
    def get(self):
        df: pd.DataFrame = Service().filter("C3", None, "bridged").resolve()
        items_count = df.shape[0]
        df = df.head(PAGE_SIZE)
        pages_count = math.ceil(items_count / PAGE_SIZE)
        current_page = 0
        return {
            "items": df.to_dict('records'),
            "items_count": items_count,
            "current_page": current_page,
            "pages_count": pages_count
        }
