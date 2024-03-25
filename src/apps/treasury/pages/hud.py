import os

import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash_extensions.enrich import html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.apps.treasury.util.constants import BCT_ERC20_CONTRACT
from src.apps.treasury.data.protocol_metrics import \
    sg, last_metric, get_last_asset_price_by_address

ILLIQUID_ASSETS_GSHEET = 'https://docs.google.com/spreadsheets/d/1beNgV2Aemu01I-iyTsfOvHDTSevb0dj8GWXqo5KDShk'

dash.register_page(__name__, title="KlimaDAO Treasury Heads Up Display")

# TODO: add caching

# TODO: combine repetitive queries to `last_metric` into a single DF call and unpack instead
# last_metric_df = sg.query_df([last_metric.marketCap, last_metric.treasuryMarketValue, ...])

# Market Cap indicator
metric_fig = go.Figure(
    go.Indicator(
        mode="number",
        value=sg.query([last_metric.marketCap]),
        number={"prefix": "$", "valueformat": ".2s"},
        title={
            "text":
            ("<a title='KLIMA supply multiplied by current price' href="
             "'https://www.coinbase.com/learn/crypto-basics/what-is-market-cap'>"
             "Market Cap</a>")
        },
        domain={'y': [0, 0.5], 'x': [0.25, 0.75]},
    )
)

metric_fig.add_trace(
    # Total Treasury Market Value ($) indicator
    go.Indicator(
        mode="number",
        value=sg.query([last_metric.treasuryMarketValue]),
        number={"prefix": "$", "valueformat": ".2s"},
        title={
            "text":
            "Treasury <a href='https://en.wikipedia.org/wiki/Market_value'>Market Value</a>"
        },
        domain={'y': [0.5, 1], 'x': [0.25, 0.75]},
    )
)

# Green Ratio status

# Pull manual illiquid asset balances from Google Sheet
illiquid_assets = pd.read_csv(
    os.path.join(ILLIQUID_ASSETS_GSHEET, 'export?gid=0&format=csv'),
    # Set first column as rownames in data frame
    index_col=0,
    # Parse column values to datetime
    parse_dates=['Date_Purchased'],
    skiprows=1
)

# Reformat fields
illiquid_assets['Dollars'] = (
    illiquid_assets.Dollars.str.replace(r'\$|,', '', regex=True).astype(float)
)
illiquid_assets['Is_Spot'] = illiquid_assets.Is_Spot.astype('bool')


# Compute total forwards balance
total_forwards = illiquid_assets[~illiquid_assets.Is_Spot]["Dollars"].sum()

# Compute total illiquid spot credit balance
total_illiquid_spot = illiquid_assets[illiquid_assets.Is_Spot]["Dollars"].sum()

# Pull sum of DAO and Treasury USDC holdings for OpEx
dao_usdc, treasury_usdc = sg.query([last_metric.daoBalanceUSDC, last_metric.treasuryBalanceUSDC])
total_usdc = dao_usdc + treasury_usdc

# Total treasury market value
# TODO: check that treasuryMarketValue field includes all assets (raw carbon, all LPs, raw KLIMA)
# TODO: add Solid World CRISP-C LP value
# TODO: add offchain assets (added illiquid spot tonnes, may be other assets)
(treasury_value, dao_klima, klima_price) = sg.query([
    last_metric.treasuryMarketValue, last_metric.daoBalanceKLIMA,
    last_metric.klimaPrice
])

# Add DAO KLIMA holdings since it is not considered part of OpEx bucket
total_treasury_value = (
    treasury_value + (dao_klima * klima_price) + total_illiquid_spot
)

# TODO: make sure treasury KLIMA is included in treasuryMarketValue

# Separate out enough lowest price carbon tonnes from total treasury value
# to back all KLIMA supply as Carbon Backing
klima_supply = sg.query([last_metric.totalSupply])

# TODO: Replace hard-coded BCT with dynamic check for lowest priced tonne
lowest_price_carbon_addr = BCT_ERC20_CONTRACT
lowest_carbon_price = get_last_asset_price_by_address(BCT_ERC20_CONTRACT)

# TODO: implement logic to loop over treasury carbon reserves from
# lowest to highest price until all KLIMA tokens are backed
# backing = 0
# while backing < klima_supply:
#    this_carbon_balance = get_last_treasury_balance_by_address(lowest_price_carbon_addr)
#    if this_carbon_balance > backing:
#        break
# TODO: add logic to sum up balances until all KLIMA tokens are backed

carbon_backing_usd = klima_supply * lowest_carbon_price
treasury_value -= carbon_backing_usd

# TODO: add descriptive tooltips to each label on the pie chart
green_ratio_data = [
    {"bucket": "Op Ex", "value": total_usdc, "target": 0.1},
    {"bucket": "Carbon Forwards", "value": total_forwards, "target": 0.22},
    {"bucket": "Carbon Backing", "value": carbon_backing_usd, "target": 0.2},
    {"bucket": "Treasury Holdings", "value": treasury_value, "target": 0.48}
]
green_ratio_df = pd.DataFrame.from_records(green_ratio_data)
order = [
    'Op Ex', 'Carbon Forwards',
    'Carbon Backing', 'Treasury Holdings'
]


# TODO: style holdings as $xx.yy[m/k] (i.e. human-formatted like indicators)
# TODO: visualize targets in some way
# TODO: load targets from Google Sheet for ease of maintenance
green_ratio_fig = px.pie(
    green_ratio_df, values="value",
    names="bucket", hole=.3, color="bucket",
    color_discrete_map={
        'Op Ex': '#f2ae00',
        'Carbon Forwards': '#6fff93',
        'Carbon Backing': '#00cc33',
        'Treasury Holdings': '#ddf641'
    },
    category_orders={'bucket': order},
    title="Green Ratio: Current",
)
green_ratio_fig.update_layout(
    title_x=0.5,
    legend=dict(
        yanchor='bottom',
        y=-.5,
        xanchor='auto',
        x=.5
    )
)

green_ratio_target_fig = px.pie(
    green_ratio_df, values="target",
    names="bucket", hole=.3, color="bucket",
    color_discrete_map={
        'Op Ex': '#f2ae00',
        'Carbon Forwards': '#6fff93',
        'Carbon Backing': '#00cc33',
        'Treasury Holdings': '#ddf641'
    },
    category_orders={'bucket': order},
    title="<a href='https://forum.klimadao.finance/d/285-rfc-green-ratio'>Green Ratio: Target</a>",
)
green_ratio_target_fig.update_layout(
    title_x=0.5,
    legend=dict(
        yanchor='bottom',
        y=-.5,
        xanchor='auto',
        x=.5
    )
)

layout = dbc.Container([
    html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=metric_fig)
            ], xs=12, sm=12, md=12, lg=4, xl=4),
            dbc.Col([
                dcc.Graph(figure=green_ratio_fig)
            ], xs=12, sm=6, md=6, lg=4, xl=4),
            dbc.Col([
                dcc.Graph(figure=green_ratio_target_fig)
            ], xs=12, sm=6, md=6, lg=4, xl=4)
        ]),
        dbc.Row([
            dbc.Col([
                html.H3(
                    html.A(
                        'Learn more',
                        href='https://dune.com/Cujowolf/Klima-DAO'
                    )
                )
            ], xs=12, sm=12, md=12, lg=12, xl=12)
        ])
    ], className='center')
], id='page_content_hud', fluid=True)
