from datetime import datetime, timedelta
import json
import os

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
import requests
from subgrounds.schema import TypeRef
from subgrounds.subgraph import SyntheticField
from subgrounds.subgrounds import Subgrounds
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

last_5_metrics = metric_query.protocolMetrics(
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
    reward_yield_df = sg.query_df([last_5_metrics.nextEpochRebase])
    avg_yield = float(reward_yield_df.mean().values[0])

    return avg_yield / 100


# TODO: finish implementing when Cujo updates the Subgraph to include MCO2
# def get_avg_cc_per_klima(days=5):
#     cc_df = sg.query_df([last_5_metrics.treasuryRiskFreeValue, last_5_metrics.totalSupply])
#     avg_cc = float(
#         (cc_df['protocolMetrics_treasuryRiskFreeValue'] / cc_df['protocolMetrics_totalSupply']).mean()
#     )
#     return avg_cc

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
    # cc_per_klima = get_avg_cc_per_klima()

    epoch_length = get_blocks_per_epoch()
    rebases_per_day = get_rebases_per_day(epoch_length)

    return price, rebase_yield, rebases_per_day


data = get_data()
avg_price = data[0]

# Dashboard
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="KLIMA Offset Yield Calculator",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'
    }]
)


input_card = dbc.Card(
    [
        dbc.CardHeader(html.H2("Input Parameters")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Monthly Carbon Emissions to Offset"),
                        dbc.CardBody([
                            dbc.InputGroup([
                                dbc.Input(placeholder="tonnes to offset", type="number", id="input-tonnes"),
                                dbc.InputGroupText(" tonnes"),
                            ])
                        ])
                    ])
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("KLIMA => Carbon Offset Conversion Factor"),
                        dbc.CardBody([
                            dbc.InputGroup([
                                dbc.Select(
                                    options=[
                                        {
                                            "label": "Intrinsic Value: 1 tonne per KLIMA (most conservative)",
                                            "value": 1
                                        },
                                        # TODO: add option for current CC
                                        {
                                            "label": (
                                                f"Market Value in BCT: {avg_price:,.2f} tonnes per KLIMA "
                                                f"at recent prices (fluctuates with market activity)"
                                            ),
                                            "value": avg_price
                                        },
                                    ],
                                    placeholder="How many tonnes do you assume each KLIMA is worth?",
                                    id="input-conversion"
                                ),
                            ])
                        ])
                    ])
                )
            ])
        ]),
    ]
)


growth_per_klima_card = dbc.Card(
    [
        dbc.CardBody([
            dbc.CardHeader("Estimated Monthly Rebase Yield"),
            dbc.CardBody("Loading...", id="monthly-return-per-klima")
        ]),
    ]
)


output_cards = [
    dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(html.H3(f"{x}x Monthly Emissions")),
                dbc.CardBody("Loading...", id=f"klima-required-{x}x")
            ]
        ),
    )
    for x in [1, 2, 3]
]


app.layout = html.Div([
    dbc.Row(dbc.Col(
        dbc.Alert(
            "WARNING: THIS TOOL IS STILL UNDER DEVELOPMENT!",
            color="warning", style={'textAlign': 'center'}
        )
    )),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.Row([
                    dbc.Col(html.Img(src='assets/KlimaDAO-Logo-Green.png', width=100, height=100), width=1),
                    dbc.Col(html.H1("Klima Infinity Yield-Based Offsetting Estimator", className='page-title'))
                ]),
                body=True
            )
        ),
        dbc.Col(growth_per_klima_card, width=3)
    ]),
    dbc.Row(dbc.Col(input_card)),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H2("Estimated Staked KLIMA to Offset Monthly Emissions with Rebase Yield")),
                dbc.CardBody([dbc.Row([*output_cards])])
            ])
        )
    ]),
    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'}, children=data),
    dcc.Interval(
        id="interval-component",
        interval=60*60*1000,  # 1 hour in milliseconds,
        n_intervals=0
    )
])


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
    monthly_roi_rounded = f"{round(monthly_roi * 100, 2)}% per month"

    if tonnes_to_offset is None or conversion_factor is None:
        return (monthly_roi_rounded, "--", "--", "--")

    klima_principal = round((tonnes_to_offset / monthly_roi) / float(conversion_factor), 2)

    return (
        monthly_roi_rounded, str(klima_principal) + ' sKLIMA',
        str(2 * klima_principal) + ' sKLIMA', str(3 * klima_principal) + ' sKLIMA'
    )


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
