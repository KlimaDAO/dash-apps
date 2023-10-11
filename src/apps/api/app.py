from flask import Flask, make_response
import json
from . import endpoints
from . import api_helpers
from src.apps import services

# Initialize app
app = Flask(__name__)
api = api_helpers.DashApi(app, prefix="/api/v1")


# Initialize cache
services.init_app(app)


# Override json serialization
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, indent=2, default=api_helpers.json_default_serializer), code)
    resp.headers.extend(headers or {})
    return resp


# Define endoints
api.add_resource(endpoints.CreditsRaw, '/credits/raw')
api.add_resource(endpoints.CreditsGlobalAggregation, '/credits/agg')
api.add_resource(endpoints.CreditsDatesAggregation, '/credits/agg/<string:freq>')
api.add_resource(endpoints.CreditsCountriesAggregation, '/credits/agg/country')
api.add_resource(endpoints.CreditsProjectsAggregation, '/credits/agg/project')
api.add_resource(endpoints.CreditsMethodologiesAggregation, '/credits/agg/methodology')
api.add_resource(endpoints.CreditsVintageAggregation, '/credits/agg/vintage')
api.add_resource(endpoints.CreditsPoolAggregation, '/credits/agg/pool')
api.add_resource(endpoints.CreditsPoolVintageAggregation, '/credits/agg/pool/vintage')
api.add_resource(endpoints.CreditsPoolMethodologyAggregation, '/credits/agg/pool/methodology')
api.add_resource(endpoints.CreditsPoolDatesAggregation, '/credits/agg/pool/<string:freq>')
api.add_resource(endpoints.CreditsBridgeVintageAggregation, '/credits/agg/bridge/vintage')
api.add_resource(endpoints.CreditsBridgeCountriesAggregation, '/credits/agg/bridge/country')
api.add_resource(endpoints.CreditsBridgeDateAggregation, '/credits/agg/bridge/<string:freq>')
api.add_resource(endpoints.CreditsBridgeAggregation, '/credits/agg/bridge')


api.add_resource(endpoints.PoolsRaw, '/pools/raw')
api.add_resource(endpoints.PoolsGlobalAggregation, '/pools/agg')
api.add_resource(endpoints.PoolsDatesAggregation, '/pools/agg/<string:freq>')
api.add_resource(endpoints.PoolsTokensAndDatesAggregation, '/pools/agg/tokens/<string:freq>')


api.add_resource(endpoints.Holders, '/holders')

api.add_resource(endpoints.Prices, '/prices')

api.add_resource(endpoints.Tokens, '/tokens')

api.add_resource(endpoints.CarbonMetrics, '/carbon_metrics/<string:chain>')

api.add_resource(endpoints.RetirementsRaw, '/retirements/<string:filter>/raw')

api.add_resource(endpoints.RetirementsGlobalAggregation, '/retirements/<string:filter>/agg')
api.add_resource(endpoints.RetirementsDatesAggregation, '/retirements/<string:filter>/agg/<string:freq>')
api.add_resource(endpoints.RetirementsTokensAggregation, '/retirements/klima/agg/tokens')
api.add_resource(endpoints.RetirementsTokensAndDatesAggregation, '/retirements/klima/agg/tokens/<string:freq>')
api.add_resource(endpoints.RetirementsBeneficiariesAggregation, '/retirements/<string:filter>/agg/beneficiary')
api.add_resource(endpoints.RetirementsOriginAndDatesAggregation, '/retirements/all/agg/origin/<string:freq>')


api.add_resource(endpoints.Info, '', '/')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
