from flask import Flask, make_response
from flask_restful import Resource, Api
import pandas as pd
import json
from . import endpoints
from src.apps.services import services_slow_cache, services_fast_cache, layout_cache
from datetime import date, datetime

app = Flask(__name__)
api = Api(app)
services_slow_cache.init_app(app)
services_fast_cache.init_app(app)
layout_cache.init_app(app)


# Fixes for json serialisation of date and datetime
def json_default_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (pd.Period)):
        return obj.to_timestamp().to_pydatetime()
    raise Exception("Type %s not serializable" % type(obj))


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, indent=2, default=json_default_serializer), code)
    resp.headers.extend(headers or {})
    return resp


class Info(Resource):
    def get(self):
        return endpoints.subendpoints_help([
            "offsets/raw",
            "offsets/agg/daily"
            ])


api.add_resource(endpoints.OffsetsRaw, '/offsets/raw')
api.add_resource(endpoints.OffsetsGlobalAggregation, '/offsets/agg')
api.add_resource(endpoints.OffsetsDateAggregation, '/offsets/agg/<string:freq>')
api.add_resource(endpoints.OffsetsCountriesAggregation, '/offsets/agg/countries')
api.add_resource(endpoints.OffsetsProjectsAggregation, '/offsets/agg/projects')
api.add_resource(endpoints.OffsetsMethodologiesAggregation, '/offsets/agg/methodologies')
api.add_resource(endpoints.Holders, '/holders')
api.add_resource(endpoints.Prices, '/prices')
api.add_resource(endpoints.CarbonMetrics, '/carbon_metrics/<string:bridge>')
api.add_resource(endpoints.RetirementsRaw, '/retirements/raw')
api.add_resource(endpoints.RetirementsDateAggregation, '/retirements/agg/<string:freq>')

api.add_resource(Info, '/')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8051)
