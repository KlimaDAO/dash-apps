from flask import Flask, make_response
from flask_restful import Resource, Api
import json
from .endpoints import Offsets
from src.apps.services import services_slow_cache, services_fast_cache
from datetime import date, datetime

app = Flask(__name__)
api = Api(app)
services_slow_cache.init_app(app)
services_fast_cache.init_app(app)


# Fixes for json serialisation of date and datetime
def json_default_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise Exception("Type %s not serializable" % type(obj))


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, indent=2, default=json_default_serializer), code)
    resp.headers.extend(headers or {})
    return resp


class Info(Resource):
    def get(self):
        return {
            'api': 'dash-api',
            'version': '0.0.1',
            'endpoints': ["offsets"],
            'help': 'use <api_url>/<endpoint>?help for assistance'
        }


api.add_resource(Offsets, '/offsets')
api.add_resource(Info, '/')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8051)
