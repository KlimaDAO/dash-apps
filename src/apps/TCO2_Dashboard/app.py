import dash_bootstrap_components as dbc
import dash
from dash import html, Input, Output, callback
from dash import dcc
from .figures import sub_plots_vintage, sub_plots_volume, map, total_vintage, total_volume, \
                     methodology_volume, pool_pie_chart, eligible_pool_pie_chart
from .figures_carbon_pool import deposited_over_time, redeemed_over_time
from .tco2 import create_content_toucan
from .bct import create_content_bct
from .helpers import date_manipulations, region_manipulations, subsets, drop_duplicates, filter_carbon_pool
from .data_related_constants import rename_map, retires_rename_map, deposits_rename_map, redeems_rename_map
from subgrounds.subgrounds import Subgrounds
from flask_caching import Cache


app = dash.Dash(title="KlimaDAO Tokenized Carbon Dashboard", suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
TIMEOUT = 86400


@cache.memoize(timeout=TIMEOUT)
def get_data():

    sg = Subgrounds()
    carbon_data = sg.load_subgraph(
        'https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

    carbon_offsets = carbon_data.Query.carbonOffsets(
        orderBy=carbon_data.CarbonOffset.lastUpdate,
        orderDirection='desc',
        first=999
    )

    df_bridged = sg.query_df([
        carbon_offsets.tokenAddress,
        carbon_offsets.region,
        carbon_offsets.vintage,
        carbon_offsets.projectID,
        carbon_offsets.standard,
        carbon_offsets.methodology,
        carbon_offsets.balanceBCT,
        carbon_offsets.balanceNCT,
        carbon_offsets.totalBridged,
        carbon_offsets.bridges.value,
        carbon_offsets.bridges.timestamp
    ])

    carbon_offsets = carbon_data.Query.retires(
        first=999
    )

    df_retired = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.offset.tokenAddress,
        carbon_offsets.offset.region,
        carbon_offsets.offset.vintage,
        carbon_offsets.offset.projectID,
        carbon_offsets.offset.standard,
        carbon_offsets.offset.methodology,
        carbon_offsets.offset.standard,
        carbon_offsets.offset.totalRetired,
    ])

    return df_bridged, df_retired


@cache.memoize(timeout=TIMEOUT)
def get_data_pool():

    sg = Subgrounds()
    carbon_data = sg.load_subgraph(
        'https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

    carbon_offsets = carbon_data.Query.deposits(
        first=999
    )

    df_deposited = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.pool,
        # carbon_offsets.offset.region,
    ])

    carbon_offsets = carbon_data.Query.redeems(
        first=999
    )

    df_redeemed = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.pool,
        # carbon_offsets.offset.region
    ])

    return df_deposited, df_redeemed


df, df_retired = get_data()
df_deposited, df_redeemed = get_data_pool()


# -----TCO2_Figures-----

# rename_columns
df = df.rename(columns=rename_map)
df_retired = df_retired.rename(columns=retires_rename_map)
# datetime manipulations
df = date_manipulations(df)
df_retired = date_manipulations(df_retired)
# Blacklist manipulations
# df = black_list_manipulations(df)
# df_retired = black_list_manipulations(df_retired)
# Region manipulations
df = region_manipulations(df)
df_retired = region_manipulations(df_retired)
# 7 day and 30 day subsets
sd_pool, last_sd_pool, td_pool, last_td_pool = subsets(df)
sd_pool_retired, last_sd_pool_retired, td_pool_retired, last_td_pool_retired = subsets(
    df_retired)
# drop duplicates data for Carbon Pool calculations
df_carbon = drop_duplicates(df)

# Summary
fig_pool_pie_chart = pool_pie_chart(df_carbon)

# Figures
# 7-day-performance
fig_seven_day_volume = sub_plots_volume(
    sd_pool, last_sd_pool, title_indicator="Credits Bridged (7d)", title_graph="")
fig_seven_day_volume_retired = sub_plots_volume(
    sd_pool_retired, last_sd_pool_retired, "Credits Retired (7d)", "")
fig_seven_day_vintage = sub_plots_vintage(
    sd_pool, last_sd_pool, "Average Credit Vintage (7d)", "")
fig_seven_day_vintage_retired = sub_plots_vintage(
    sd_pool_retired, last_sd_pool_retired, "Average Credit Vintage (7d)", "")
fig_seven_day_map = map(
    sd_pool, 'Where have the past 7-day credits originated from?')
fig_seven_day_map_retired = map(
    sd_pool_retired, 'Where were the past 7-day retired credits originated from?')
fig_seven_day_metho = methodology_volume(sd_pool)
fig_seven_day_metho_retired = methodology_volume(sd_pool_retired)

# 30-day-performance
fig_thirty_day_volume = sub_plots_volume(
    td_pool, last_td_pool, "Credits Bridged (30d)", "")
fig_thirty_day_volume_retired = sub_plots_volume(
    td_pool_retired, last_td_pool_retired, "Credits Retired (30d)", "")
fig_thirty_day_vintage = sub_plots_vintage(
    td_pool, last_td_pool, "Average Credit Vintage (30d)", "")
fig_thirty_day_vintage_retired = sub_plots_vintage(
    td_pool_retired, last_td_pool_retired, "Average Credit Vintage (30d)", "")
fig_thirty_day_map = map(
    td_pool, 'Where have the past 30-day credits originated from?')
fig_thirty_day_map_retired = map(
    td_pool_retired, 'Where were the past 30-day retired credits originated from?')
fig_thirty_day_metho = methodology_volume(td_pool)
fig_thirty_day_metho_retired = methodology_volume(td_pool_retired)

# Total
fig_total_volume = total_volume(df)
fig_total_volume_retired = total_volume(df_retired)
fig_total_vintage = total_vintage(df)
fig_total_vintage_retired = total_vintage(df_retired)
fig_total_map = map(df, 'Where have all the past credits originated from?')
fig_total_map_retired = map(
    df_retired, 'Where were all the past retired credits originated from?')
fig_total_metho = methodology_volume(df)
fig_total_metho_retired = methodology_volume(df_retired)

content_tco2 = create_content_toucan(df, df_retired, fig_pool_pie_chart)


# --Carbon Pool Figures---

# rename_columns
df_deposited = df_deposited.rename(columns=deposits_rename_map)
df_redeemed = df_redeemed.rename(columns=redeems_rename_map)
# datetime manipulations
df_deposited = date_manipulations(df_deposited)
df_redeemed = date_manipulations(df_redeemed)
# Blacklist manipulations
# df_deposited = black_list_manipulations(df_deposited)
# df_redeemed = black_list_manipulations(df_redeemed)

# Carbon pool filter
bct_deposited, bct_redeemed = filter_carbon_pool(
    df_deposited, df_redeemed, "0x2f800db0fdb5223b3c3f354886d907a671414a7f")

# Figures
fig_deposited_over_time = deposited_over_time(bct_deposited)
fig_redeemed_over_time = redeemed_over_time(bct_redeemed)

content_bct = create_content_bct(
    bct_deposited, bct_redeemed, fig_deposited_over_time, fig_redeemed_over_time)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": '#232B2B',
    "font-size": 20
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        dbc.Col(html.Img(src='assets/KlimaDAO-Logo.png',
                width=200, height=200), width=12),
        html.H3("Dashboards", style={'text-align': 'center'}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("TCO2", href="/", active="exact",
                            className="pill-nav"),
                dbc.NavLink("BCT", href="/BCT", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@callback(
    Output(component_id='Last X Days', component_property='children'),
    Output(component_id='volume plot', component_property='figure'),
    Output(component_id='vintage plot', component_property='figure'),
    Output(component_id='map', component_property='figure'),
    Output(component_id="fig_total_metho", component_property='children'),
    Input(component_id='summary_type', component_property='value'),
    Input(component_id='bridged_or_retired', component_property='value')
)
def update_output_div(summary_type, TCO2_type):
    if summary_type == 'Last 7 Days Performance':
        if TCO2_type == 'Bridged':
            return "Last 7 Days Performance", fig_seven_day_volume, fig_seven_day_vintage, fig_seven_day_map, \
                    dcc.Graph(figure=fig_seven_day_metho)
        elif TCO2_type == 'Retired':
            return "Last 7 Days Performance", fig_seven_day_volume_retired, fig_seven_day_vintage_retired, \
                 fig_seven_day_map_retired, dcc.Graph(figure=fig_seven_day_metho_retired)

    elif summary_type == 'Last 30 Days Performance':
        if TCO2_type == 'Bridged':
            return "Last 30 Days Performance", fig_thirty_day_volume, fig_thirty_day_vintage, fig_thirty_day_map, \
                 dcc.Graph(figure=fig_thirty_day_metho)
        elif TCO2_type == 'Retired':
            return "Last 30 Days Performance", fig_thirty_day_volume_retired, fig_thirty_day_vintage_retired, \
                 fig_thirty_day_map_retired, dcc.Graph(figure=fig_thirty_day_metho_retired)

    elif summary_type == 'Overall Performance':
        if TCO2_type == 'Bridged':
            return "Overall Performance", fig_total_volume, fig_total_vintage, fig_total_map,\
                dcc.Graph(figure=fig_total_metho)
        elif TCO2_type == 'Retired':
            return "Overall Performance", fig_total_volume_retired, fig_total_vintage_retired, fig_total_map_retired, \
                dcc.Graph(figure=fig_total_metho_retired)


@callback(
    Output(component_id='eligible pie chart plot',
           component_property='figure'),
    Input(component_id='pie_chart_summary', component_property='value')
)
def update_eligible_pie_chart(pool_key):
    fig_eligible_pool_pie_chart = eligible_pool_pie_chart(df_carbon, pool_key)
    return fig_eligible_pool_pie_chart


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return content_tco2

    elif pathname == "/BCT":
        return content_bct

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# For Gunicorn to reference
server = app.server


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
