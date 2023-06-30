from flask import Flask
from flask_restful import Resource, Api
from .endpoints import Offsets
from src.apps.services import services_slow_cache, services_fast_cache

app = Flask(__name__)
api = Api(app)
services_slow_cache.init_app(app)
services_fast_cache.init_app(app)


class Info(Resource):
    def get(self):
        return {'api': 'dash-api'}


api.add_resource(Offsets, '/offsets')
api.add_resource(Info, '/')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8051)
