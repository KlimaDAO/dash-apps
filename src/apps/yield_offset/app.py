from datetime import datetime, timedelta
import json
import os
from re import A

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
import requests
from subgrounds.plotly_wrappers import Scatter, Figure
from subgrounds.dash_wrappers import Graph
from subgrounds.schema import TypeRef
from subgrounds.subgraph import SyntheticField
from subgrounds.subgrounds import Subgrounds
from web3 import Web3
from web3.middleware import geth_poa_middleware


from ...constants import DISTRIBUTOR_ADDRESS
from ...util import get_polygon_web3, load_abi

SCAN_API_KEY = os.environ['POLYGONSCAN_API_KEY']


INFURA_PROJ_ID = os.environ['WEB3_INFURA_PROJECT_ID']


# Initialize web3
web3 = get_polygon_web3()
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load ABIs
DISTRIBUTOR_ABI = load_abi('distributor.json')


# Load Subgraphs
sg = Subgrounds()
markets = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/0xplaygrounds/playgrounds-klima-markets')
metrics = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/cujowolf/klima-graph')


# This is unecessary, but nice for brevity
market_query = markets.Query
Trade = markets.Trade
metric_query = metrics.Query
Metric = metrics.ProtocolMetric

# This is a synthetic field
Trade.datetime = SyntheticField(
    lambda timestamp: str(datetime.fromtimestamp(timestamp)),
    TypeRef.Named('String'),
    Trade.timestamp,
)

Metric.datetime = SyntheticField(
    lambda timestamp: str(datetime.fromtimestamp(timestamp)),
    TypeRef.Named('String'),
    Metric.timestamp,
)

trades = market_query.trades(
    orderBy=Trade.timestamp,
    orderDirection='desc',
    first=500,
    where=[
        Trade.pair == '0x9803c7ae526049210a1725f7487af26fe2c24614'
    ]
)

last_30_metrics = metric_query.protocolMetrics(
    orderBy=Metric.timestamp,
    orderDirection='desc',
    first=5
)

# Price & APY calculations
def get_blocks_per_epoch():
    distributor_contract = web3.eth.contract(
        address=DISTRIBUTOR_ADDRESS,
        abi=DISTRIBUTOR_ABI
    )
    return distributor_contract.functions.epochLength().call()


def get_block_30_days_ago():
    '''Fetch the block number that was closest to 30 days ago from PolygonScan'''
    days_ago = datetime.today() - timedelta(days=30)
    timestamp = int(days_ago.timestamp())

    resp = requests.get(
        f'https://api.polygonscan.com/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={SCAN_API_KEY}'  # noqa: E501
    )

    block_num = int(
        json.loads(resp.content)['result']
    )

    return block_num


def get_rebases_per_day(blocks_per_rebase):
    '''
    Calculates the average number of rebases per day based on the average
    block production time for the previous 1 million blocks
    '''
    block_30_days_ago = get_block_30_days_ago()

    latest_block = web3.eth.get_block('latest')
    latest_block_num = latest_block['number']
    latest_block_time = latest_block['timestamp']

    prev_block_time = web3.eth.get_block(block_30_days_ago)['timestamp']

    block_diff = latest_block_num - block_30_days_ago
    avg_block_secs = (latest_block_time - prev_block_time) / block_diff

    secs_per_rebase = blocks_per_rebase * avg_block_secs

    return 24 / (secs_per_rebase / 60 / 60)


def get_avg_yield(days=5):
    reward_yield_df = sg.query_df([last_30_metrics.nextEpochRebase])
    avg_yield = float(reward_yield_df.mean().values[0])

    return avg_yield / 100


def get_avg_price(days=30):
    trades = market_query.trades(
        orderBy=Trade.timestamp,
        orderDirection='desc',
        first=days,
        where=[
            Trade.pair == '0x9803c7ae526049210a1725f7487af26fe2c24614'
        ]
    )

    price_df = sg.query_df([trades.close])
    return price_df.mean().values[0]


def get_data():
    price = get_avg_price()
    rebase_yield = get_avg_yield()

    epoch_length = get_blocks_per_epoch()
    rebases_per_day = get_rebases_per_day(epoch_length)

    return price, rebase_yield, rebases_per_day


data = get_data()
avg_price = data[0]

# Dashboard
app = dash.Dash(__name__)

app.layout = html.Div(
    html.Div([
        html.H1("Klima Price in BCT Terms"),
        html.Div([
            Graph(Figure(
                subgrounds=sg,
                traces=[
                    Scatter(x=trades.datetime, y=trades.close)
                ]
            ))
        ]),
        html.H1("APY Over Time"),
        html.Div([
            Graph(Figure(
                subgrounds=sg,
                traces=[
                    Scatter(x=last_30_metrics.datetime, y=last_30_metrics.currentAPY)
                ]
            ))
        ]),
        html.Div([
            dbc.InputGroup([
                dbc.InputGroupText("Monthly Carbon Footprint to Offset: "),
                dbc.Input(placeholder="tonnes to offset", type="number", id="input-tonnes"),
                dbc.InputGroupText(" tonnes"),
            ]),
            dbc.InputGroup([
                dbc.InputGroupText("KLIMA => tonnes of CO2 Conversion Factor: "),
                dbc.Select(
                    options=[
                        {"label": "Intrinsic Value: 1 tonne per KLIMA (most conservative)", "value": 1},
                        {
                            "label": (
                                f"Market Value in BCT: {avg_price:,.2f} tonnes per KLIMA "
                                f"at recent prices (fluctuates with market activity)"
                            ),
                            "value": avg_price
                        },
                    ],
                    id="input-conversion"
                ),
            ]),
            html.H2("Monthly Rebase Growth Per KLIMA: "),
            html.Div(id="monthly-return-per-klima"),
            html.Div([
                html.Div([
                    html.H2(f"Amount of staked KLIMA required to capture {x}x footprint via rebase rewards:"),
                    html.Div(id=f"klima-required-{x}x")
                ])
                for x in [1, 2, 3]
            ])
        ]),
        # Hidden div inside the app that stores the intermediate value
        html.Div(id='intermediate-value', style={'display': 'none'}, children = data),
        dcc.Interval(
            id="interval-component",
            interval=10*1000, # in milliseconds,
            n_intervals=0
        )
    ])
)


x_outputs = [
    Output(f"klima-required-{x}x", "children") for x in [1, 2, 3]
]


@app.callback(
    Output('intermediate-value', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    return get_data()


@app.callback(
    Output("monthly-return-per-klima", "children"),
    *x_outputs,
    Input("input-tonnes", "value"),
    Input("input-conversion", "value"),
    Input('intermediate-value', 'children')
)
def cb_render(*vals):
    tonnes_to_offset = vals[0]
    conversion_factor = vals[1]
    data = vals[2]
    price, reward_yield, rebases_per_day = data

    # 30 day ROI
    monthly_roi = (1 + reward_yield) ** (30 * rebases_per_day) - 1
    # monthly_roi_perc = round(monthly_roi * 100, 1)

    if tonnes_to_offset is None or conversion_factor is None:
        return (monthly_roi, "--", "--", "--")

    klima_principal = (tonnes_to_offset / monthly_roi) / float(conversion_factor)

    return (monthly_roi, klima_principal, 2 * klima_principal, 3 * klima_principal)


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
