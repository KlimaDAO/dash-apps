import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output

from datetime import datetime

from subgrounds.plotly_wrappers import Scatter, Figure
from subgrounds.dash_wrappers import Graph
from subgrounds.schema import TypeRef
from subgrounds.subgraph import SyntheticField
from subgrounds.subgrounds import Subgrounds


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


avg_price_on_load = get_avg_price()

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
                                f"Market Value in BCT: {avg_price_on_load:,.2f} tonnes per KLIMA "
                                f"at recent prices (fluctuates with market activity)"
                            ),
                            "value": avg_price_on_load
                        },
                    ],
                    id="input-conversion"
                ),
            ]),
            html.H2("Monthly Rebase Growth Per KLIMA: "),
            html.Div(id="monthly-return-per-klima"),
            html.Div([
                html.Div([
                    html.H2(f"Amount of staked KLIMA required to capture {x}x footprint via rebases:"),
                    html.Div(id=f"klima-required-{x}x")
                ])
                for x in [1, 2, 3]
            ])
        ])
    ])
)


x_outputs = [
    Output(f"klima-required-{x}x", "children") for x in [1, 2, 3]
]


@app.callback(
    Output("monthly-return-per-klima", "children"),
    *x_outputs,
    Input("input-tonnes", "value"),
    Input("input-conversion", "value")
)
def cb_render(*vals):
    tonnes_to_offset = vals[0]
    conversion_factor = vals[1]

    # TODO: switch to use `nextEpochRebase` and PolygonScan for avg blocktime
    # DO NOT CALL ON EVERY CALLBACK CALL!
    apy_df = sg.query_df([last_30_metrics.currentAPY])
    avg_apy = float(apy_df.mean().values[0])

    reward_yield = ((1 + avg_apy / 100) ** (1 / float(1095))) - 1
    reward_yield = round(reward_yield, 5)

    # 30 day ROI
    monthly_roi = (1 + reward_yield) ** (30 * 3) - 1
    # monthly_roi_perc = round(monthly_roi * 100, 1)

    if tonnes_to_offset is None or conversion_factor is None:
        return (monthly_roi, "--", "--", "--")

    klima_principal = (tonnes_to_offset / monthly_roi) / float(conversion_factor)

    return (monthly_roi, klima_principal, 2 * klima_principal, 3 * klima_principal)


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
