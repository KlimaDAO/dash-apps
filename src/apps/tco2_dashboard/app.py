import dash_bootstrap_components as dbc
import dash
import pandas as pd
from dash import html, Input, Output, callback
from dash import dcc
from .figures import sub_plots_vintage, sub_plots_volume, map, total_vintage, total_volume, \
    methodology_volume, project_volume, pool_pie_chart, eligible_pool_pie_chart
from .figures_carbon_pool import deposited_over_time, redeemed_over_time
from .tco2 import create_content_toucan
from .bct import create_content_bct
from .helpers import date_manipulations, region_manipulations, subsets, drop_duplicates, filter_carbon_pool, \
    bridge_manipulations, merge_verra
from .data_related_constants import rename_map, retires_rename_map, deposits_rename_map, redeems_rename_map, \
    verra_rename_map, merge_columns
from subgrounds.subgrounds import Subgrounds
from flask_caching import Cache
import requests

CACHE_TIMEOUT = 10000
CARBON_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon'
MAX_RECORDS = 400

ORIGIN_MAP_TITLE_PREFIX = 'Origin of Credits'

app = dash.Dash(
    __name__,
    title="KlimaDAO Tokenized Carbon Dashboard",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Configure cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DIR': '/tmp/cache-directory',
    'CACHE_DEFAULT_TIMEOUT': CACHE_TIMEOUT
})


@cache.memoize()
def get_data():

    sg = Subgrounds()
    carbon_data = sg.load_subgraph(CARBON_SUBGRAPH_URL)

    carbon_offsets = carbon_data.Query.carbonOffsets(
        orderBy=carbon_data.CarbonOffset.lastUpdate,
        orderDirection='desc',
        first=MAX_RECORDS
    )

    df_bridged = sg.query_df([
        carbon_offsets.tokenAddress,
        carbon_offsets.bridge,
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
        first=MAX_RECORDS
    )

    df_retired = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.offset.tokenAddress,
        carbon_offsets.offset.bridge,
        carbon_offsets.offset.region,
        carbon_offsets.offset.vintage,
        carbon_offsets.offset.projectID,
        carbon_offsets.offset.standard,
        carbon_offsets.offset.methodology,
        carbon_offsets.offset.standard,
        carbon_offsets.offset.totalRetired,
    ])

    return df_bridged, df_retired


@cache.memoize()
def get_data_pool():

    sg = Subgrounds()
    carbon_data = sg.load_subgraph(CARBON_SUBGRAPH_URL)

    carbon_offsets = carbon_data.Query.deposits(
        first=MAX_RECORDS
    )

    df_deposited = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.pool,
        # carbon_offsets.offset.region,
    ])

    carbon_offsets = carbon_data.Query.redeems(
        first=MAX_RECORDS
    )

    df_redeemed = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.pool,
        # carbon_offsets.offset.region
    ])

    return df_deposited, df_redeemed


@cache.memoize()
def get_verra_data():
    r = requests.post(
        'https://registry.verra.org/uiapi/asset/asset/search?$maxResults=2000&$count=true&$skip=0&format=csv',
        json={"program": "VCS", "issuanceTypeCodes": ['ISSUE']})
    df_verra = pd.DataFrame(r.json()['value']).rename(columns=verra_rename_map)
    df_verra.loc[df_verra['Retirement Details'].str.contains(
        'TOUCAN').fillna(False), 'Toucan'] = True
    df_verra['Toucan'] = df_verra['Toucan'].fillna(False)
    return df_verra


def generate_layout():
    df, df_retired = get_data()
    print(df)
    df_deposited, df_redeemed = get_data_pool()
    df_verra = get_verra_data()
    # -----TCO2_Figures-----

    # rename_columns
    df = df.rename(columns=rename_map)
    df_retired = df_retired.rename(columns=retires_rename_map)
    # merge Verra Data
    df = merge_verra(df, df_verra, merge_columns)
    df_retired = merge_verra(df_retired, df_verra, merge_columns)
    # datetime manipulations
    df = date_manipulations(df)
    df_retired = date_manipulations(df_retired)
    # Blacklist manipulations
    # df = black_list_manipulations(df)
    # df_retired = black_list_manipulations(df_retired)
    # Bridge manipulations
    df = bridge_manipulations(df, "Toucan")
    df_retired = bridge_manipulations(df_retired, "Toucan")
    # Region manipulations
    df = region_manipulations(df)
    df_retired = region_manipulations(df_retired)
    # 7 day and 30 day subsets
    sd_pool, last_sd_pool, td_pool, last_td_pool = subsets(df)
    sd_pool_retired, last_sd_pool_retired, td_pool_retired, last_td_pool_retired = subsets(
        df_retired)
    # drop duplicates data for Carbon Pool calculations
    df_carbon = drop_duplicates(df)
    cache.set("df_carbon", df_carbon)

    # Summary
    fig_pool_pie_chart = pool_pie_chart(df_carbon)
    cache.set("fig_pool_pie_chart", fig_pool_pie_chart)

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
        sd_pool, ORIGIN_MAP_TITLE_PREFIX + ' Bridged in the Last 7 Days')
    fig_seven_day_map_retired = map(
        sd_pool_retired, ORIGIN_MAP_TITLE_PREFIX + ' Retired in the Last 7 Days')
    fig_seven_day_metho = methodology_volume(sd_pool)
    fig_seven_day_metho_retired = methodology_volume(sd_pool_retired)
    fig_seven_day_project = project_volume(sd_pool)
    fig_seven_day_project_retired = project_volume(sd_pool_retired)

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
        td_pool, ORIGIN_MAP_TITLE_PREFIX + ' Bridged in the Last 30 Days')
    fig_thirty_day_map_retired = map(
        td_pool_retired, ORIGIN_MAP_TITLE_PREFIX + ' Retired in the Last 7 Days')
    fig_thirty_day_metho = methodology_volume(td_pool)
    fig_thirty_day_metho_retired = methodology_volume(td_pool_retired)
    fig_thirty_day_project = project_volume(td_pool)
    fig_thirty_day_project_retired = project_volume(td_pool_retired)

    # Total
    fig_total_volume = total_volume(df, "Credits tokenized (total)")
    fig_total_volume_retired = total_volume(
        df_retired, "Credits retired (total)")
    fig_total_vintage = total_vintage(df)
    fig_total_vintage_retired = total_vintage(df_retired)
    fig_total_map = map(df, ORIGIN_MAP_TITLE_PREFIX + ' Bridged')
    fig_total_map_retired = map(
        df_retired, ORIGIN_MAP_TITLE_PREFIX + ' Retired')
    fig_total_metho = methodology_volume(df)
    fig_total_metho_retired = methodology_volume(df_retired)
    fig_total_project = project_volume(df)
    fig_total_project_retired = project_volume(df_retired)

    content_tco2 = create_content_toucan(df, df_retired, fig_pool_pie_chart)

    fig_seven_day = [fig_seven_day_volume, fig_seven_day_vintage,
                     fig_seven_day_map, fig_seven_day_metho, fig_seven_day_project]
    fig_seven_day_retired = [fig_seven_day_volume_retired, fig_seven_day_vintage_retired,
                             fig_seven_day_map_retired, fig_seven_day_metho_retired, fig_seven_day_project_retired]
    fig_thirty_day = [fig_thirty_day_volume, fig_thirty_day_vintage,
                      fig_thirty_day_map, fig_thirty_day_metho, fig_thirty_day_project]
    fig_thirty_day_retired = [fig_thirty_day_volume_retired, fig_thirty_day_vintage_retired,
                              fig_thirty_day_map_retired, fig_thirty_day_metho_retired, fig_thirty_day_project_retired]
    fig_total = [fig_total_volume, fig_total_vintage,
                 fig_total_map, fig_total_metho, fig_total_project]
    fig_total_retired = [fig_total_volume_retired, fig_total_vintage_retired,
                         fig_total_map_retired, fig_total_metho_retired, fig_total_project_retired]

    cache.set("fig_seven_day", fig_seven_day)
    cache.set("fig_seven_day_retired", fig_seven_day_retired)
    cache.set("fig_thirty_day", fig_thirty_day)
    cache.set("fig_thirty_day_retired", fig_thirty_day_retired)
    cache.set("fig_total", fig_total)
    cache.set("fig_total_retired", fig_total_retired)
    cache.set("content_tco2", content_tco2)

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

    cache.set("content_bct", content_bct)

    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "backgroundColor": '#232B2B',
        "fontSize": 20
    }

    CONTENT_STYLE = {
        "marginLeft": "18rem",
        "marginRight": "2rem",
        "padding": "2rem 1rem",
    }

    sidebar = html.Div(
        [
            dbc.Col(html.Img(src='assets/KlimaDAO-Wordmark.png', width=200),
                    width=12, style={'textAlign': 'center'}),
            html.H3("Tokenized Carbon Dashboards",
                    style={'textAlign': 'center'}),
            html.Hr(),
            html.H4("Toucan Protocol", style={'textAlign': 'center'}),
            dbc.Nav(
                [
                    dbc.NavLink("TCO2 Overview", href="/", active="exact",
                                className="pill-nav"),
                    dbc.NavLink("BCT Pool", href="/BCT", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

    layout = html.Div([dcc.Location(id="url"), sidebar, content])
    return layout


app.layout = generate_layout


@callback(
    Output(component_id='Last X Days', component_property='children'),
    Output(component_id='volume plot', component_property='figure'),
    Output(component_id='vintage plot', component_property='figure'),
    Output(component_id='map', component_property='figure'),
    Output(component_id="methodology", component_property='figure'),
    Output(component_id="projects", component_property='figure'),
    Input(component_id='summary_type', component_property='value'),
    Input(component_id='bridged_or_retired', component_property='value')
)
def update_output_div(summary_type, TCO2_type):
    if summary_type == 'Last 7 Days Performance':
        if TCO2_type == 'Bridged':
            fig_seven_day = cache.get("fig_seven_day")
            return "Last 7 Days Performance", fig_seven_day[0], fig_seven_day[1], fig_seven_day[2], \
                fig_seven_day[3], fig_seven_day[4]
        elif TCO2_type == 'Retired':
            fig_seven_day_retired = cache.get("fig_seven_day_retired")
            return "Last 7 Days Performance", fig_seven_day_retired[0], fig_seven_day_retired[1], \
                fig_seven_day_retired[2], fig_seven_day_retired[3], fig_seven_day_retired[4]

    elif summary_type == 'Last 30 Days Performance':
        if TCO2_type == 'Bridged':
            fig_thirty_day = cache.get("fig_thirty_day")
            return "Last 30 Days Performance", fig_thirty_day[0], fig_thirty_day[1], fig_thirty_day[2], \
                fig_thirty_day[3], fig_thirty_day[4]
        elif TCO2_type == 'Retired':
            fig_thirty_day_retired = cache.get("fig_thirty_day_retired")
            return "Last 30 Days Performance", fig_thirty_day_retired[0], fig_thirty_day_retired[1], \
                fig_thirty_day_retired[2], fig_thirty_day_retired[3], fig_thirty_day_retired[4]

    elif summary_type == 'Lifetime Performance':
        if TCO2_type == 'Bridged':
            fig_total = cache.get("fig_total")
            return "Lifetime Performance", fig_total[0], fig_total[1], fig_total[2],\
                fig_total[3], fig_total[4]
        elif TCO2_type == 'Retired':
            fig_total_retired = cache.get("fig_total_retired")
            return "Lifetime Performance", fig_total_retired[0], fig_total_retired[1], fig_total_retired[2],\
                fig_total_retired[3], fig_total_retired[4]


@callback(
    Output(component_id='eligible pie chart plot',
           component_property='figure'),
    Input(component_id='pie_chart_summary', component_property='value')
)
def update_eligible_pie_chart(pool_key):
    df_carbon = cache.get("df_carbon")
    fig_eligible_pool_pie_chart = eligible_pool_pie_chart(df_carbon, pool_key)
    return fig_eligible_pool_pie_chart


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        content_tco2 = cache.get("content_tco2")
        return content_tco2

    elif pathname == "/BCT":
        content_bct = cache.get("content_bct")
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
