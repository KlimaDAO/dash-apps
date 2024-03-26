from subgrounds.subgrounds import Subgrounds
from subgrounds.subgraph import SyntheticField

from src.apps.treasury.util.constants import KLIMA_PROTOCOL_SUBGRAPH
from src.apps.treasury.util.time_util import get_date_timestamp_string

sg = Subgrounds()
protocol_metrics_subgraph = sg.load_subgraph(KLIMA_PROTOCOL_SUBGRAPH)

# Define useful synthetic fields
# Protocol metrics
protocol_metrics_subgraph.ProtocolMetric.datetime = SyntheticField(
    lambda timestamp: get_date_timestamp_string(timestamp),
    SyntheticField.STRING,
    protocol_metrics_subgraph.ProtocolMetric.timestamp,
)

# Treasury asset
protocol_metrics_subgraph.TreasuryAsset.datetime = SyntheticField(
    lambda timestamp: get_date_timestamp_string(timestamp),
    SyntheticField.STRING,
    protocol_metrics_subgraph.TreasuryAsset.timestamp,
)

protocol_metrics_subgraph.TreasuryAsset.formatted_market_value = SyntheticField(
    lambda marketValue: round(marketValue / float(1000000), 4),
    SyntheticField.FLOAT,
    protocol_metrics_subgraph.TreasuryAsset.marketValue,
)

last_metric = protocol_metrics_subgraph.Query.protocolMetrics(
    orderBy=protocol_metrics_subgraph.ProtocolMetric.timestamp,
    orderDirection='desc',
    first=1
)


def get_last_asset_price_by_address(address):
    last_balance = protocol_metrics_subgraph.Query.treasuryAssets(
        orderBy=protocol_metrics_subgraph.TreasuryAsset.timestamp,
        orderDirection='desc',
        first=1,
        where=[protocol_metrics_subgraph.TreasuryAsset.token == address]
    )

    protocol_metrics_subgraph.TreasuryAsset.market_price = (
        protocol_metrics_subgraph.TreasuryAsset.marketValue /
        protocol_metrics_subgraph.TreasuryAsset.tokenBalance
    )

    return sg.query([last_balance.market_price])
