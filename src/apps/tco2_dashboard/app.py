import dash_bootstrap_components as dbc
import dash
from dash import html, Input, Output, callback, State
from dash import dcc
from flask_caching import Cache
import pandas as pd
import requests
from subgrounds.subgrounds import Subgrounds
from ...util import get_eth_web3, load_abi

from .figures import sub_plots_vintage, sub_plots_volume, map, total_vintage, total_volume, \
    methodology_volume, project_volume, eligible_pool_pie_chart, project_volume_mco2
from .figures_carbon_pool import deposited_over_time, redeemed_over_time
from .tco2 import create_content_toucan
from .pool import create_pool_content
from .mco2 import create_content_moss
from .helpers import date_manipulations, filter_pool_quantity, region_manipulations, \
    subsets, drop_duplicates, filter_carbon_pool, bridge_manipulations, \
    merge_verra, verra_manipulations, mco2_verra_manipulations, read_csv
from .constants import rename_map, retires_rename_map, deposits_rename_map, \
    redeems_rename_map, BCT_ADDRESS, \
    verra_rename_map, merge_columns, mco2_verra_rename_map, MCO2_ADDRESS, verra_columns, \
    VERRA_FALLBACK_NOTE, VERRA_FALLBACK_URL, NCT_ADDRESS

CACHE_TIMEOUT = 86400
CARBON_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon'
MAX_RECORDS = 1000000

app = dash.Dash(
    __name__,
    title="KlimaDAO Tokenized Carbon Dashboard | Beta",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

# Configure cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DIR': '/tmp/cache-directory',
    'CACHE_DEFAULT_TIMEOUT': CACHE_TIMEOUT
})


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


def get_verra_data():
    use_fallback_data = False
    if use_fallback_data:
        fallback_note = VERRA_FALLBACK_NOTE
        df_verra = pd.read_csv(VERRA_FALLBACK_URL)
        df_verra = df_verra[verra_columns]
    else:
        try:
            fallback_note = ""
            r = requests.post(
                'https://registry.verra.org/uiapi/asset/asset/search?$maxResults=2000&$count=true&$skip=0&format=csv',
                json={"program": "VCS", "issuanceTypeCodes": ['ISSUE']})
            df_verra = pd.DataFrame(r.json()['value']).rename(columns=verra_rename_map)
        except requests.exceptions.RequestException as err:
            print(err)
            fallback_note = VERRA_FALLBACK_NOTE
            df_verra = pd.read_csv(VERRA_FALLBACK_URL)
            df_verra = df_verra[verra_columns]
    return df_verra, fallback_note


web3 = get_eth_web3()


def get_mco2_contract_data():
    ERC20_ABI = load_abi('erc20.json')
    mco2_contract = web3.eth.contract(address=MCO2_ADDRESS, abi=ERC20_ABI)
    decimals = 10 ** mco2_contract.functions.decimals().call()
    total_supply = mco2_contract.functions.totalSupply().call() // decimals
    return total_supply


@cache.memoize()
def generate_layout():
    df, df_retired = get_data()
    df_deposited, df_redeemed = get_data_pool()
    df_verra, verra_fallback_note = get_verra_data()
    df_verra, df_verra_toucan = verra_manipulations(df_verra)
    df_mco2_bridged = read_csv('mco2_verra_data.csv')
    mco2_current_supply = get_mco2_contract_data()
    # -----TCO2_Figures-----
    # rename_columns
    df = df.rename(columns=rename_map)
    df_retired = df_retired.rename(columns=retires_rename_map)
    df_mco2_bridged = df_mco2_bridged.rename(columns=mco2_verra_rename_map)
    # merge Verra Data
    df = merge_verra(df, df_verra_toucan, merge_columns)
    df_retired = merge_verra(df_retired, df_verra, merge_columns)
    # datetime manipulations
    df = date_manipulations(df, "Toucan")
    df_retired = date_manipulations(df_retired, "Toucan")
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

    # Figures
    # 7-day-performance
    zero_bridging_evt_text = "There haven't been any bridging events<br>in the last 7 days"
    zero_retiring_evt_text = "There haven't been any retiring events<br>in the last 7 days"
    fig_seven_day_volume = sub_plots_volume(
        sd_pool, last_sd_pool, "Credits Bridged (7d)", "", zero_bridging_evt_text)
    fig_seven_day_volume_retired = sub_plots_volume(
        sd_pool_retired, last_sd_pool_retired, "Credits Retired (7d)", "", zero_retiring_evt_text)
    fig_seven_day_vintage = sub_plots_vintage(
        sd_pool, last_sd_pool, "Average Credit Vintage (7d)", "", zero_bridging_evt_text)
    fig_seven_day_vintage_retired = sub_plots_vintage(
        sd_pool_retired, last_sd_pool_retired, "Average Credit Vintage (7d)", "",
        zero_retiring_evt_text)
    fig_seven_day_map = map(
        sd_pool, zero_bridging_evt_text)
    fig_seven_day_map_retired = map(
        sd_pool_retired, zero_retiring_evt_text)
    fig_seven_day_metho = methodology_volume(sd_pool, zero_bridging_evt_text)
    fig_seven_day_metho_retired = methodology_volume(
        sd_pool_retired, zero_retiring_evt_text)
    fig_seven_day_project = project_volume(sd_pool, zero_bridging_evt_text)
    fig_seven_day_project_retired = project_volume(
        sd_pool_retired, zero_retiring_evt_text)

    # 30-day-performance
    zero_bridging_evt_text = "There haven't been any bridging events<br>in the last 30 days"
    zero_retiring_evt_text = "There haven't been any retiring events<br>in the last 30 days"
    fig_thirty_day_volume = sub_plots_volume(
        td_pool, last_td_pool, "Credits Bridged (30d)", "", zero_bridging_evt_text)
    fig_thirty_day_volume_retired = sub_plots_volume(
        td_pool_retired, last_td_pool_retired, "Credits Retired (30d)", "", zero_retiring_evt_text)
    fig_thirty_day_vintage = sub_plots_vintage(
        td_pool, last_td_pool, "Average Credit Vintage (30d)", "", zero_bridging_evt_text)
    fig_thirty_day_vintage_retired = sub_plots_vintage(
        td_pool_retired, last_td_pool_retired, "Average Credit Vintage (30d)", "", zero_retiring_evt_text)
    fig_thirty_day_map = map(td_pool, zero_bridging_evt_text)
    fig_thirty_day_map_retired = map(td_pool_retired, zero_retiring_evt_text)
    fig_thirty_day_metho = methodology_volume(
        td_pool, zero_bridging_evt_text)
    fig_thirty_day_metho_retired = methodology_volume(
        td_pool_retired, zero_retiring_evt_text)
    fig_thirty_day_project = project_volume(td_pool, zero_bridging_evt_text)
    fig_thirty_day_project_retired = project_volume(
        td_pool_retired, zero_retiring_evt_text)

    # Total
    zero_bridging_evt_text = "There haven't been any<br>bridging events"
    zero_retiring_evt_text = "There haven't been any<br>retiring events"
    fig_total_volume = total_volume(
        df, "Credits tokenized (total)", zero_bridging_evt_text)
    fig_total_volume_retired = total_volume(
        df_retired, "Credits retired (total)", zero_retiring_evt_text)
    fig_total_vintage = total_vintage(df, zero_bridging_evt_text)
    fig_total_vintage_retired = total_vintage(
        df_retired, zero_retiring_evt_text)
    fig_total_map = map(df, zero_bridging_evt_text)
    fig_total_map_retired = map(
        df_retired, zero_retiring_evt_text)
    fig_total_metho = methodology_volume(df, zero_bridging_evt_text)
    fig_total_metho_retired = methodology_volume(
        df_retired, zero_retiring_evt_text)
    fig_total_project = project_volume(df, zero_bridging_evt_text)
    fig_total_project_retired = project_volume(
        df_retired, zero_retiring_evt_text)

    content_tco2 = create_content_toucan(
        df, df_retired, df_carbon, df_verra, df_verra_toucan, verra_fallback_note)

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

    # --MCO2 Figures--
    df_mco2_bridged = df_mco2_bridged.rename(columns=mco2_verra_rename_map)
    df_mco2_bridged = mco2_verra_manipulations(df_mco2_bridged)
    fig_mco2_total_vintage = total_vintage(
        df_mco2_bridged, zero_bridging_evt_text)
    fig_mco2_total_project = project_volume_mco2(df_mco2_bridged, zero_bridging_evt_text)
    content_mco2 = create_content_moss(df_mco2_bridged, fig_mco2_total_vintage, fig_mco2_total_project,
                                       mco2_current_supply)
    cache.set("content_mco2", content_mco2)

    # --Carbon Pool Figures---

    # rename_columns
    df_deposited = df_deposited.rename(columns=deposits_rename_map)
    df_redeemed = df_redeemed.rename(columns=redeems_rename_map)
    # datetime manipulations
    df_deposited = date_manipulations(df_deposited, "")
    df_redeemed = date_manipulations(df_redeemed, "")
    # Blacklist manipulations
    # df_deposited = black_list_manipulations(df_deposited)
    # df_redeemed = black_list_manipulations(df_redeemed)

    # --BCT---

    # Carbon pool filter
    bct_deposited, bct_redeemed = filter_carbon_pool(
        BCT_ADDRESS, df_deposited, df_redeemed
    )
    bct_carbon = filter_pool_quantity(df_carbon, "BCT Quantity")

    # BCT Figures
    fig_deposited_over_time = deposited_over_time(bct_deposited)
    fig_redeemed_over_time = redeemed_over_time(bct_redeemed)

    content_bct = create_pool_content(
        "BCT", "Base Carbon Tonne", bct_deposited, bct_redeemed, bct_carbon,
        fig_deposited_over_time, fig_redeemed_over_time
    )

    cache.set("content_bct", content_bct)

    # --NCT--

    # Carbon pool filter
    nct_deposited, nct_redeemed = filter_carbon_pool(
        NCT_ADDRESS, df_deposited, df_redeemed
    )

    nct_carbon = filter_pool_quantity(df_carbon, "NCT Quantity")

    # NCT Figures
    fig_deposited_over_time = deposited_over_time(nct_deposited)
    fig_redeemed_over_time = redeemed_over_time(nct_redeemed)

    content_nct = create_pool_content(
        "NCT", "Nature Carbon Tonne", nct_deposited, nct_redeemed, nct_carbon,
        fig_deposited_over_time, fig_redeemed_over_time
    )

    cache.set("content_nct", content_nct)

    sidebar_toggle = dbc.Row(
        [
            dbc.Col(
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    style={
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="toggle",
                ),
                width="auto", align="center",
            ),
        ]
    )

    sidebar_header = html.Div([dbc.Col(
        html.A([
            html.Img(src='assets/KlimaDAO-Wordmark.png', width=200)
        ], href='https://www.klimadao.finance/'),
        width=12, style={'textAlign': 'center'}),
        html.H3("Tokenized Carbon Dashboards Beta",
                style={'textAlign': 'center'}),
    ], id="logo_title")

    sidebar = html.Div(
        [sidebar_header,
            sidebar_toggle,
            dbc.Collapse(children=[
                dbc.Nav(
                    [html.Hr(),
                        html.H4("Toucan Protocol", style={
                                'textAlign': 'center'}),
                        dbc.NavLink("TCO2 Overview", href="/", active="exact",
                                    className="pill-nav", id="button-tco2", n_clicks=0),
                        dbc.NavLink("BCT Pool", href="/BCT", active="exact",
                                    id="button-bct", n_clicks=0),
                        dbc.NavLink("NCT Pool", href="/NCT", active="exact",
                                    id="button-nct", n_clicks=0),
                        html.H4("Moss Protocol", style={
                                'textAlign': 'center'}),
                        dbc.NavLink("MCO2 Overview", href="/MCO2", active="exact",
                                    id="button-mco2", n_clicks=0),
                     ],
                    vertical=True,
                    pills=True,
                )],
                id="collapse",
            ),
         ],
        id="sidebar",
    )

    content = html.Div(id="page-content", children=[],
                       )

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

    elif pathname == "/NCT":
        content_nct = cache.get("content_nct")
        return content_nct

    elif pathname == "/MCO2":
        content_mco2 = cache.get("content_mco2")
        return content_mco2

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


@app.callback(
    Output("collapse", "is_open"),
    [Input("toggle", "n_clicks"),
     Input("button-tco2", "n_clicks"),
     Input("button-bct", "n_clicks"),
     Input("button-nct", "n_clicks"),
     Input("button-mco2", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, n_tco2, n_bct, n_nct, n_mco2, is_open):
    if n or n_tco2 or n_bct or n_nct or n_mco2:
        return not is_open
    return is_open


# For Gunicorn to reference
server = app.server


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
