from flask_restful import Resource
from . import subendpoints_help


class Info(Resource):
    """Returns subendpoints"""
    def get(self):
        return subendpoints_help([
            "credits/raw",
            "credits/agg",
            "credits/agg/daily",
            "credits/agg/monthly",
            "credits/agg/countriy",
            "credits/agg/project",
            "credits/agg/methodology",
            "credits/agg/vintage",
            "credits/agg/pool",
            "credits/agg/pool/vintage",
            "credits/agg/pool/methodology",
            "credits/agg/pool/project",
            "credits/agg/pool/daily",
            "credits/agg/pool/monthly",
            "credits/agg/bridge/vintage",
            "credits/agg/bridge/country",
            "credits/agg/bridge/project",
            "credits/agg/bridge/daily",
            "credits/agg/bridge/monthly",
            "pools/raw",
            "pools/agg",
            "pools/agg/daily",
            "pools/agg/monthly",
            "holders",
            "prices",
            "tokens",
            "carbon_metrics/polygon",
            "carbon_metrics/eth",
            "carbon_metrics/celo",
            "retirements/all/raw",
            "retirements/all/agg",
            "retirements/all/agg/daily",
            "retirements/all/agg/monthly",
            "retirements/all/agg/beneficiary",
            "retirements/all/agg/origin/daily",
            "retirements/all/agg/origin/monthly",
            "retirements/klima/raw",
            "retirements/klima/agg",
            "retirements/klima/agg/daily",
            "retirements/klima/agg/monthly",
            "retirements/klima/agg/beneficiary",
            "retirements/klima/agg/tokens",
            "retirements/klima/agg/tokens/daily",
            "retirements/klima/agg/tokens/monthly"
        ])
