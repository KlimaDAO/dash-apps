from datetime import datetime
import os

import dash_bootstrap_components as dbc
import dash
from dash import html, Input, Output, callback, State
from dash import dcc
from flask_caching import Cache
import pandas as pd
import requests
from subgrounds.subgrounds import Subgrounds
from pycoingecko import CoinGeckoAPI

# from ...util import get_eth_web3, load_abi
from .figures import sub_plots_vintage, sub_plots_volume, map, total_vintage, total_volume, \
    methodology_volume, project_volume, eligible_pool_pie_chart, pool_pie_chart,\
    historical_prices, bridges_pie_chart, on_vs_off_vintage, on_vs_off_map, on_vs_off_project,\
    tokenized_volume, on_vs_off_vintage_retired, on_vs_off_map_retired, on_vs_off_project_retired
from .figures_carbon_pool import deposited_over_time, redeemed_over_time, retired_over_time
from .offchain_vs_onchain import create_offchain_vs_onchain_content
from .onchain_pool_comp import create_onchain_pool_comp_content
from .tco2 import create_content_toucan
from .c3t import create_content_c3t
from .pool import create_pool_content
from .mco2 import create_content_moss
from .helpers import date_manipulations, filter_pool_quantity, region_manipulations, \
    subsets, drop_duplicates, filter_carbon_pool, bridge_manipulations, \
    merge_verra, verra_manipulations, mco2_verra_manipulations, \
    adjust_mco2_bridges, verra_retired, date_manipulations_verra
from .constants import rename_map, retires_rename_map, deposits_rename_map, \
    redeems_rename_map, pool_retires_rename_map, BCT_ADDRESS, \
    verra_rename_map, merge_columns, MCO2_ADDRESS, verra_columns, \
    VERRA_FALLBACK_NOTE, VERRA_FALLBACK_URL, NCT_ADDRESS, KLIMA_RETIRED_NOTE, UBO_ADDRESS, \
    NBO_ADDRESS, mco2_bridged_rename_map, bridges_rename_map

CACHE_TIMEOUT = 86400
CARBON_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/klimadao/polygon-bridged-carbon'
CARBON_MOSS_ETH_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/originalpkbims/ethcarbonsubgraph'
CARBON_ETH_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/originalpkbims/ethereum-bridged-carbon'
MAX_RECORDS = 1000000
PRICE_DAYS = 5000
GOOGLE_API_ICONS = {
    'href': "https://fonts.googleapis.com/icon?family=Material+Icons", 'rel': "stylesheet"}

# Configure plausible.io tracking script
external_scripts = [
    {
        'src': 'https://plausible.io/js/script.js',
        'data-domain': 'carbon.klimadao.finance'
    }
] if os.environ.get('ENV') == 'Production' else []

app = dash.Dash(
    __name__,
    title="KlimaDAO Tokenized Carbon Dashboard | Beta",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, GOOGLE_API_ICONS],
    external_scripts=external_scripts,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"property": "og:type", "content": "website"},
        {"property": "og:site_name", "content": "KlimaDAO Carbon Dashboards"},
        {"property": "og:title", "content": "State of Tokenized Carbon"},
        {
            "property": "og:description",
            "content":
            """
            Data visualizations, analytics and detailed drilldowns
            into the state of the on-chain carbon markets in the Ethereum ecosystem.
            """
        },
        {
            "property": "og:image",
            "content": "https://www.klimadao.finance/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fdk34t4vc%2Fproduction%2F0be338e1930c5bf36101feaa7669c8330057779a-2156x1080.png&w=1920&q=75"  # noqa: E501
        },
        {"name": "twitter:card", "content": "summary_large_image"},
        {"name": "twitter:site", "content": "@discord"},
        {"name": "twitter:creator", "content": "@KlimaDAO"}
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
        carbon_offsets.country,
        carbon_offsets.category,
        carbon_offsets.name,
        carbon_offsets.balanceBCT,
        carbon_offsets.balanceNCT,
        carbon_offsets.balanceUBO,
        carbon_offsets.balanceNBO,
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
        carbon_offsets.offset.country,
        carbon_offsets.offset.category,
        carbon_offsets.offset.name,
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


def get_data_pool_retired():

    sg = Subgrounds()
    carbon_data = sg.load_subgraph(CARBON_SUBGRAPH_URL)

    klimaretires = carbon_data.Query.klimaRetires(
        first=MAX_RECORDS
    )

    df_pool_retired = sg.query_df([
        klimaretires.timestamp,
        klimaretires.pool,
        klimaretires.amount,
    ])

    return df_pool_retired


def get_mco2_data():
    sg = Subgrounds()

    carbon_data = sg.load_subgraph(CARBON_MOSS_ETH_SUBGRAPH_URL)
    carbon_offsets = carbon_data.Query.batches(
        first=MAX_RECORDS
    )
    df_bridged = sg.query_df([
        carbon_offsets.id,
        carbon_offsets.serialNumber,
        carbon_offsets.timestamp,
        carbon_offsets.tokenAddress,
        carbon_offsets.vintage,
        carbon_offsets.projectID,
        carbon_offsets.value,
        carbon_offsets.originaltx,
    ])

    carbon_data = sg.load_subgraph(CARBON_ETH_SUBGRAPH_URL)
    carbon_offsets = carbon_data.Query.bridges(
        first=MAX_RECORDS
    )
    df_bridged_tx = sg.query_df([
        carbon_offsets.value,
        carbon_offsets.timestamp,
        carbon_offsets.transaction.id,
    ])

    carbon_data = sg.load_subgraph(CARBON_ETH_SUBGRAPH_URL)
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
        carbon_offsets.offset.country,
        carbon_offsets.offset.category,
        carbon_offsets.offset.name,
        carbon_offsets.offset.totalRetired,
    ])
    return df_bridged, df_bridged_tx, df_retired


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
            df_verra = pd.DataFrame(r.json()['value']).rename(
                columns=verra_rename_map)
        except requests.exceptions.RequestException as err:
            print(err)
            fallback_note = VERRA_FALLBACK_NOTE
            df_verra = pd.read_csv(VERRA_FALLBACK_URL)
            df_verra = df_verra[verra_columns]
    return df_verra, fallback_note


# web3 = get_eth_web3() if os.environ.get('WEB3_INFURA_PROJECT_ID') else None


# def get_mco2_contract_data():
#     ERC20_ABI = load_abi('erc20.json')
#     if web3 is not None:
#         mco2_contract = web3.eth.contract(address=MCO2_ADDRESS, abi=ERC20_ABI)
#         decimals = 10 ** mco2_contract.functions.decimals().call()
#         total_supply = mco2_contract.functions.totalSupply().call() // decimals
#         return total_supply
#     else:
#         # If web3 is not connected, just return an invalid value
#         return -1


cg = CoinGeckoAPI()
token_cg_dict = {
    'BCT': {'address': BCT_ADDRESS, 'id': 'polygon-pos', 'Full Name': 'Base Carbon Tonne'},
    'NCT': {'address': NCT_ADDRESS, 'id': 'polygon-pos', 'Full Name': 'Nature Carbon Tonne'},
    'MCO2': {'address': MCO2_ADDRESS, 'id': 'ethereum', 'Full Name': 'Moss Carbon Credit'},
}


def get_prices():
    df_prices = pd.DataFrame()
    for i in token_cg_dict.keys():
        data = cg.get_coin_market_chart_from_contract_address_by_id(
            id=token_cg_dict[i]['id'], vs_currency='usd', contract_address=token_cg_dict[i]['address'], days=PRICE_DAYS)
        df = pd.DataFrame(data['prices'], columns=['Date', f'{i}_Price'])
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        df['Date'] = df['Date'].dt.floor('D')
        if df_prices.empty:
            df_prices = df
        else:
            df_prices = df_prices.merge(df, how='outer', on='Date')
        df_prices = df_prices.sort_values(by='Date', ascending=False)
    return df_prices


@cache.memoize()
def generate_layout():
    df, df_retired = get_data()
    df_deposited, df_redeemed = get_data_pool()
    df_pool_retired = get_data_pool_retired()
    df_bridged_mco2, df_bridged_tx_mco2, df_retired_mco2 = get_mco2_data()
    df_verra, verra_fallback_note = get_verra_data()
    df_verra, df_verra_toucan, df_verra_c3 = verra_manipulations(df_verra)
    df_prices = get_prices()
    curr_time_str = datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")

    # rename_columns
    df = df.rename(columns=rename_map)
    df_retired = df_retired.rename(columns=retires_rename_map)

    # -----TCO2_Figures----
    # Bridge manipulations
    df_tc = bridge_manipulations(df, "Toucan")
    df_retired_tc = bridge_manipulations(df_retired, "Toucan")
    # merge Verra Data
    df_tc = merge_verra(df_tc, df_verra_toucan, merge_columns, [
                        'Name', 'Country', 'Project Type'])
    df_retired_tc = merge_verra(df_retired_tc, df_verra, merge_columns, [
                                'Name', 'Country', 'Project Type'])
    # datetime manipulations
    df_tc = date_manipulations(df_tc)
    df_retired_tc = date_manipulations(df_retired_tc)
    # Blacklist manipulations
    # df = black_list_manipulations(df)
    # df_retired = black_list_manipulations(df_retired)
    # Region manipulations
    df_tc = region_manipulations(df_tc)
    df_retired_tc = region_manipulations(df_retired_tc)
    # 7 day and 30 day subsets
    sd_pool_tc, last_sd_pool_tc, td_pool_tc, last_td_pool_tc = subsets(df_tc)
    sd_pool_retired_tc, last_sd_pool_retired_tc, td_pool_retired_tc, last_td_pool_retired_tc = subsets(
        df_retired_tc)
    # drop duplicates data for Carbon Pool calculations
    df_carbon_tc = drop_duplicates(df_tc)
    cache.set("df_carbon_tc", df_carbon_tc)

    # Figures
    # 7-day-performance
    zero_bridging_evt_text = "There haven't been any bridging events<br>in the last 7 days"
    zero_retiring_evt_text = "There haven't been any retiring events<br>in the last 7 days"
    fig_seven_day_volume_tc = sub_plots_volume(
        sd_pool_tc, last_sd_pool_tc, "Credits Bridged (7d)", "", zero_bridging_evt_text)
    fig_seven_day_volume_retired_tc = sub_plots_volume(
        sd_pool_retired_tc, last_sd_pool_retired_tc, "Credits Retired (7d)", "", zero_retiring_evt_text)
    fig_seven_day_vintage_tc = sub_plots_vintage(
        sd_pool_tc, last_sd_pool_tc, "Average Credit Vintage (7d)", "", zero_bridging_evt_text)
    fig_seven_day_vintage_retired_tc = sub_plots_vintage(
        sd_pool_retired_tc, last_sd_pool_retired_tc, "Average Credit Vintage (7d)", "",
        zero_retiring_evt_text)
    fig_seven_day_map_tc = map(
        sd_pool_tc, zero_bridging_evt_text)
    fig_seven_day_map_retired_tc = map(
        sd_pool_retired_tc, zero_retiring_evt_text)
    fig_seven_day_metho_tc = methodology_volume(
        sd_pool_tc, zero_bridging_evt_text)
    fig_seven_day_metho_retired_tc = methodology_volume(
        sd_pool_retired_tc, zero_retiring_evt_text)
    fig_seven_day_project_tc = project_volume(
        sd_pool_tc, zero_bridging_evt_text)
    fig_seven_day_project_retired_tc = project_volume(
        sd_pool_retired_tc, zero_retiring_evt_text)

    # 30-day-performance
    zero_bridging_evt_text = "There haven't been any bridging events<br>in the last 30 days"
    zero_retiring_evt_text = "There haven't been any retiring events<br>in the last 30 days"
    fig_thirty_day_volume_tc = sub_plots_volume(
        td_pool_tc, last_td_pool_tc, "Credits Bridged (30d)", "", zero_bridging_evt_text)
    fig_thirty_day_volume_retired_tc = sub_plots_volume(
        td_pool_retired_tc, last_td_pool_retired_tc, "Credits Retired (30d)", "", zero_retiring_evt_text)
    fig_thirty_day_vintage_tc = sub_plots_vintage(
        td_pool_tc, last_td_pool_tc, "Average Credit Vintage (30d)", "", zero_bridging_evt_text)
    fig_thirty_day_vintage_retired_tc = sub_plots_vintage(
        td_pool_retired_tc, last_td_pool_retired_tc, "Average Credit Vintage (30d)", "", zero_retiring_evt_text)
    fig_thirty_day_map_tc = map(td_pool_tc, zero_bridging_evt_text)
    fig_thirty_day_map_retired_tc = map(
        td_pool_retired_tc, zero_retiring_evt_text)
    fig_thirty_day_metho_tc = methodology_volume(
        td_pool_tc, zero_bridging_evt_text)
    fig_thirty_day_metho_retired_tc = methodology_volume(
        td_pool_retired_tc, zero_retiring_evt_text)
    fig_thirty_day_project_tc = project_volume(
        td_pool_tc, zero_bridging_evt_text)
    fig_thirty_day_project_retired_tc = project_volume(
        td_pool_retired_tc, zero_retiring_evt_text)

    # Total
    zero_bridging_evt_text = "There haven't been any<br>bridging events"
    zero_retiring_evt_text = "There haven't been any<br>retiring events"
    fig_total_volume_tc = total_volume(
        df_tc, "Credits tokenized (total)", zero_bridging_evt_text)
    fig_total_volume_retired_tc = total_volume(
        df_retired_tc, "Credits retired (total)", zero_retiring_evt_text)
    fig_total_vintage_tc = total_vintage(df_tc, zero_bridging_evt_text)
    fig_total_vintage_retired_tc = total_vintage(
        df_retired_tc, zero_retiring_evt_text)
    fig_total_map_tc = map(df_tc, zero_bridging_evt_text)
    fig_total_map_retired_tc = map(
        df_retired_tc, zero_retiring_evt_text)
    fig_total_metho_tc = methodology_volume(df_tc, zero_bridging_evt_text)
    fig_total_metho_retired_tc = methodology_volume(
        df_retired_tc, zero_retiring_evt_text)
    fig_total_project_tc = project_volume(df_tc, zero_bridging_evt_text)
    fig_total_project_retired_tc = project_volume(
        df_retired_tc, zero_retiring_evt_text)

    fig_pool_pie_chart_tc = pool_pie_chart(df_carbon_tc, ['BCT', 'NCT'])
    content_tco2 = create_content_toucan(
        df_tc, df_retired_tc, fig_pool_pie_chart_tc)

    fig_seven_day_tc = [fig_seven_day_volume_tc, fig_seven_day_vintage_tc,
                        fig_seven_day_map_tc, fig_seven_day_metho_tc, fig_seven_day_project_tc]
    fig_seven_day_retired_tc = [fig_seven_day_volume_retired_tc, fig_seven_day_vintage_retired_tc,
                                fig_seven_day_map_retired_tc, fig_seven_day_metho_retired_tc,
                                fig_seven_day_project_retired_tc]
    fig_thirty_day_tc = [fig_thirty_day_volume_tc, fig_thirty_day_vintage_tc,
                         fig_thirty_day_map_tc, fig_thirty_day_metho_tc, fig_thirty_day_project_tc]
    fig_thirty_day_retired_tc = [fig_thirty_day_volume_retired_tc, fig_thirty_day_vintage_retired_tc,
                                 fig_thirty_day_map_retired_tc, fig_thirty_day_metho_retired_tc,
                                 fig_thirty_day_project_retired_tc]
    fig_total_tc = [fig_total_volume_tc, fig_total_vintage_tc,
                    fig_total_map_tc, fig_total_metho_tc, fig_total_project_tc]
    fig_total_retired_tc = [fig_total_volume_retired_tc, fig_total_vintage_retired_tc,
                            fig_total_map_retired_tc, fig_total_metho_retired_tc, fig_total_project_retired_tc]

    cache.set("fig_seven_day_tc", fig_seven_day_tc)
    cache.set("fig_seven_day_retired_tc", fig_seven_day_retired_tc)
    cache.set("fig_thirty_day_tc", fig_thirty_day_tc)
    cache.set("fig_thirty_day_retired_tc", fig_thirty_day_retired_tc)
    cache.set("fig_total_tc", fig_total_tc)
    cache.set("fig_total_retired_tc", fig_total_retired_tc)
    cache.set("content_tco2", content_tco2)

    # -----C3_Figures----
    # Bridge manipulations
    df_c3t = bridge_manipulations(df, "C3")
    df_retired_c3t = bridge_manipulations(df_retired, "C3")
    # datetime manipulations
    df_c3t = date_manipulations(df_c3t)
    df_retired_c3t = date_manipulations(df_retired_c3t)
    # Blacklist manipulations
    # df = black_list_manipulations(df)
    # df_retired = black_list_manipulations(df_retired)
    # Region manipulations
    df_c3t = region_manipulations(df_c3t)
    df_retired_c3t = region_manipulations(df_retired_c3t)
    # 7 day and 30 day subsets
    sd_pool_c3t, last_sd_pool_c3t, td_pool_c3t, last_td_pool_c3t = subsets(
        df_c3t)
    sd_pool_retired_c3t, last_sd_pool_retired_c3t, td_pool_retired_c3t, last_td_pool_retired_c3t = subsets(
        df_retired_c3t)
    # drop duplicates data for Carbon Pool calculations
    df_carbon_c3t = drop_duplicates(df_c3t)
    cache.set("df_carbon_c3t", df_carbon_c3t)

    # Figures
    # 7-day-performance
    zero_bridging_evt_text = "There haven't been any bridging events<br>in the last 7 days"
    zero_retiring_evt_text = "There haven't been any retiring events<br>in the last 7 days"
    fig_seven_day_volume_c3t = sub_plots_volume(
        sd_pool_c3t, last_sd_pool_c3t, "Credits Bridged (7d)", "", zero_bridging_evt_text)
    fig_seven_day_volume_retired_c3t = sub_plots_volume(
        sd_pool_retired_c3t, last_sd_pool_retired_c3t, "Credits Retired (7d)", "", zero_retiring_evt_text)
    fig_seven_day_vintage_c3t = sub_plots_vintage(
        sd_pool_c3t, last_sd_pool_c3t, "Average Credit Vintage (7d)", "", zero_bridging_evt_text)
    fig_seven_day_vintage_retired_c3t = sub_plots_vintage(
        sd_pool_retired_c3t, last_sd_pool_retired_c3t, "Average Credit Vintage (7d)", "",
        zero_retiring_evt_text)
    fig_seven_day_map_c3t = map(
        sd_pool_c3t, zero_bridging_evt_text)
    fig_seven_day_map_retired_c3t = map(
        sd_pool_retired_c3t, zero_retiring_evt_text)
    fig_seven_day_metho_c3t = methodology_volume(
        sd_pool_c3t, zero_bridging_evt_text)
    fig_seven_day_metho_retired_c3t = methodology_volume(
        sd_pool_retired_c3t, zero_retiring_evt_text)
    fig_seven_day_project_c3t = project_volume(
        sd_pool_c3t, zero_bridging_evt_text)
    fig_seven_day_project_retired_c3t = project_volume(
        sd_pool_retired_c3t, zero_retiring_evt_text)

    # 30-day-performance
    zero_bridging_evt_text = "There haven't been any bridging events<br>in the last 30 days"
    zero_retiring_evt_text = "There haven't been any retiring events<br>in the last 30 days"
    fig_thirty_day_volume_c3t = sub_plots_volume(
        td_pool_c3t, last_td_pool_c3t, "Credits Bridged (30d)", "", zero_bridging_evt_text)
    fig_thirty_day_volume_retired_c3t = sub_plots_volume(
        td_pool_retired_c3t, last_td_pool_retired_c3t, "Credits Retired (30d)", "", zero_retiring_evt_text)
    fig_thirty_day_vintage_c3t = sub_plots_vintage(
        td_pool_c3t, last_td_pool_c3t, "Average Credit Vintage (30d)", "", zero_bridging_evt_text)
    fig_thirty_day_vintage_retired_c3t = sub_plots_vintage(
        td_pool_retired_c3t, last_td_pool_retired_c3t, "Average Credit Vintage (30d)", "", zero_retiring_evt_text)
    fig_thirty_day_map_c3t = map(td_pool_c3t, zero_bridging_evt_text)
    fig_thirty_day_map_retired_c3t = map(
        td_pool_retired_c3t, zero_retiring_evt_text)
    fig_thirty_day_metho_c3t = methodology_volume(
        td_pool_c3t, zero_bridging_evt_text)
    fig_thirty_day_metho_retired_c3t = methodology_volume(
        td_pool_retired_c3t, zero_retiring_evt_text)
    fig_thirty_day_project_c3t = project_volume(
        td_pool_c3t, zero_bridging_evt_text)
    fig_thirty_day_project_retired_c3t = project_volume(
        td_pool_retired_c3t, zero_retiring_evt_text)

    # Total
    zero_bridging_evt_text = "There haven't been any<br>bridging events"
    zero_retiring_evt_text = "There haven't been any<br>retiring events"
    fig_total_volume_c3t = total_volume(
        df_c3t, "Credits tokenized (total)", zero_bridging_evt_text)
    fig_total_volume_retired_c3t = total_volume(
        df_retired_c3t, "Credits retired (total)", zero_retiring_evt_text)
    fig_total_vintage_c3t = total_vintage(df_c3t, zero_bridging_evt_text)
    fig_total_vintage_retired_c3t = total_vintage(
        df_retired_c3t, zero_retiring_evt_text)
    fig_total_map_c3t = map(df_c3t, zero_bridging_evt_text)
    fig_total_map_retired_c3t = map(
        df_retired_c3t, zero_retiring_evt_text)
    fig_total_metho_c3t = methodology_volume(df_c3t, zero_bridging_evt_text)
    fig_total_metho_retired_c3t = methodology_volume(
        df_retired_c3t, zero_retiring_evt_text)
    fig_total_project_c3t = project_volume(df_c3t, zero_bridging_evt_text)
    fig_total_project_retired_c3t = project_volume(
        df_retired_c3t, zero_retiring_evt_text)
    fig_pool_pie_chart_c3t = pool_pie_chart(df_carbon_c3t, ['UBO', 'NBO'])

    content_c3t = create_content_c3t(
        df_c3t, df_retired_c3t, fig_pool_pie_chart_c3t)

    fig_seven_day_c3t = [fig_seven_day_volume_c3t, fig_seven_day_vintage_c3t,
                         fig_seven_day_map_c3t, fig_seven_day_metho_c3t, fig_seven_day_project_c3t]
    fig_seven_day_retired_c3t = [fig_seven_day_volume_retired_c3t, fig_seven_day_vintage_retired_c3t,
                                 fig_seven_day_map_retired_c3t, fig_seven_day_metho_retired_c3t,
                                 fig_seven_day_project_retired_c3t]
    fig_thirty_day_c3t = [fig_thirty_day_volume_c3t, fig_thirty_day_vintage_c3t,
                          fig_thirty_day_map_c3t, fig_thirty_day_metho_c3t, fig_thirty_day_project_c3t]
    fig_thirty_day_retired_c3t = [fig_thirty_day_volume_retired_c3t, fig_thirty_day_vintage_retired_c3t,
                                  fig_thirty_day_map_retired_c3t, fig_thirty_day_metho_retired_c3t,
                                  fig_thirty_day_project_retired_c3t]
    fig_total_c3t = [fig_total_volume_c3t, fig_total_vintage_c3t,
                     fig_total_map_c3t, fig_total_metho_c3t, fig_total_project_c3t]
    fig_total_retired_c3t = [fig_total_volume_retired_c3t, fig_total_vintage_retired_c3t,
                             fig_total_map_retired_c3t, fig_total_metho_retired_c3t, fig_total_project_retired_c3t]

    cache.set("fig_seven_day_c3t", fig_seven_day_c3t)
    cache.set("fig_seven_day_retired_c3t", fig_seven_day_retired_c3t)
    cache.set("fig_thirty_day_c3t", fig_thirty_day_c3t)
    cache.set("fig_thirty_day_retired_c3t", fig_thirty_day_retired_c3t)
    cache.set("fig_total_c3t", fig_total_c3t)
    cache.set("fig_total_retired_c3t", fig_total_retired_c3t)
    cache.set("content_c3t", content_c3t)

    # --MCO2 Figures--

    df_bridged_mco2 = df_bridged_mco2.rename(columns=mco2_bridged_rename_map)
    df_verra_retired = verra_retired(df_verra, df_bridged_mco2)
    df_retired_mco2 = df_retired_mco2.rename(columns=retires_rename_map)
    df_bridged_tx_mco2 = df_bridged_tx_mco2.rename(columns=bridges_rename_map)
    df_retired_mco2 = bridge_manipulations(df_retired_mco2, "Moss")
    df_bridged_mco2["Project ID"] = 'VCS-' + \
        df_bridged_mco2["Project ID"].astype(str)
    df_bridged_mco2 = merge_verra(df_bridged_mco2, df_verra, merge_columns+['Vintage Start'], [
        'Name', 'Country', 'Project Type', 'Vintage'])
    df_bridged_mco2["Vintage"] = df_bridged_mco2['Serial Number'].astype(
        str).str[-15:-11].astype(int)
    df_retired_mco2 = merge_verra(df_retired_mco2, df_verra, merge_columns, [
        'Name', 'Country', 'Project Type'])
    df_bridged_mco2 = adjust_mco2_bridges(df_bridged_mco2, df_bridged_tx_mco2)
    df_bridged_mco2 = date_manipulations_verra(df_bridged_mco2)
    df_retired_mco2 = date_manipulations(df_retired_mco2)

    zero_bridging_evt_text = "There haven't been any<br>bridging events"
    fig_mco2_total_volume = deposited_over_time(
        df_bridged_mco2)
    fig_mco2_total_vintage = total_vintage(
        df_bridged_mco2, zero_bridging_evt_text)
    fig_mco2_total_map = map(df_bridged_mco2, zero_bridging_evt_text)
    fig_mco2_total_metho = methodology_volume(
        df_bridged_mco2, zero_bridging_evt_text)
    fig_mco2_total_project = project_volume(
        df_bridged_mco2, zero_bridging_evt_text)
    df_bridged_mco2_summary = mco2_verra_manipulations(df_bridged_mco2)
    content_mco2 = create_content_moss(df_bridged_mco2_summary, df_retired_mco2, fig_mco2_total_volume,
                                       fig_mco2_total_vintage, fig_mco2_total_map,
                                       fig_mco2_total_metho, fig_mco2_total_project)

    cache.set("content_mco2", content_mco2)

    # --Carbon Pool Figures---

    # rename_columns
    df_deposited = df_deposited.rename(columns=deposits_rename_map)
    df_redeemed = df_redeemed.rename(columns=redeems_rename_map)

    # Blacklist manipulations
    # df_deposited = black_list_manipulations(df_deposited)
    # df_redeemed = black_list_manipulations(df_redeemed)

    # rename_columns
    df_pool_retired = df_pool_retired.rename(columns=pool_retires_rename_map)
    # datetime manipulations
    df_pool_retired = date_manipulations(df_pool_retired)

    # --BCT---

    # Carbon pool filter
    bct_deposited, bct_redeemed, bct_retired = filter_carbon_pool(
        BCT_ADDRESS, df_deposited, df_redeemed, df_pool_retired
    )
    bct_deposited = date_manipulations(bct_deposited)
    bct_redeemed = date_manipulations(bct_redeemed)
    bct_carbon = filter_pool_quantity(df_carbon_tc, "BCT Quantity")

    # BCT Figures
    fig_deposited_over_time = deposited_over_time(bct_deposited)
    fig_redeemed_over_time = redeemed_over_time(bct_redeemed)
    fig_retired_over_time = retired_over_time(
        BCT_ADDRESS, 'BCT', df_pool_retired)
    zero_bridging_evt_text = "The BCT Pool is empty"
    fig_bct_total_vintage = total_vintage(
        bct_carbon, zero_bridging_evt_text)
    fig_bct_total_map = map(bct_carbon, zero_bridging_evt_text)
    fig_bct_total_metho = methodology_volume(
        bct_carbon, zero_bridging_evt_text)
    fig_bct_total_project = project_volume(
        bct_carbon, zero_bridging_evt_text)

    content_bct = create_pool_content(
        "BCT", "Base Carbon Tonne", bct_deposited, bct_redeemed, bct_retired, bct_carbon,
        fig_deposited_over_time, fig_redeemed_over_time, fig_retired_over_time, fig_bct_total_vintage,
        fig_bct_total_map, fig_bct_total_metho, fig_bct_total_project, KLIMA_RETIRED_NOTE)

    cache.set("content_bct", content_bct)

    # --NCT--

    # Carbon pool filter
    nct_deposited, nct_redeemed, nct_retired = filter_carbon_pool(
        NCT_ADDRESS, df_deposited, df_redeemed, df_pool_retired
    )
    nct_deposited = date_manipulations(nct_deposited)
    nct_redeemed = date_manipulations(nct_redeemed)
    nct_carbon = filter_pool_quantity(df_carbon_tc, "NCT Quantity")

    # NCT Figures
    fig_deposited_over_time = deposited_over_time(nct_deposited)
    fig_redeemed_over_time = redeemed_over_time(nct_redeemed)
    fig_retired_over_time = retired_over_time(
        NCT_ADDRESS, 'NCT', df_pool_retired)
    zero_bridging_evt_text = "The NCT Pool is empty"
    fig_nct_total_vintage = total_vintage(
        nct_carbon, zero_bridging_evt_text)
    fig_nct_total_map = map(nct_carbon, zero_bridging_evt_text)
    fig_nct_total_metho = methodology_volume(
        nct_carbon, zero_bridging_evt_text)
    fig_nct_total_project = project_volume(
        nct_carbon, zero_bridging_evt_text)

    content_nct = create_pool_content(
        "NCT", "Nature Carbon Tonne", nct_deposited, nct_redeemed, nct_retired, nct_carbon,
        fig_deposited_over_time, fig_redeemed_over_time, fig_retired_over_time, fig_nct_total_vintage,
        fig_nct_total_map, fig_nct_total_metho, fig_nct_total_project, KLIMA_RETIRED_NOTE)

    cache.set("content_nct", content_nct)

    # --UBO---

    # Carbon pool filter
    df_carbon_c3t["Project ID"] = 'VCS-' + \
        df_carbon_c3t["Project ID"].astype(str)
    ubo_deposited, ubo_redeemed = filter_carbon_pool(
        UBO_ADDRESS, df_deposited, df_redeemed
    )
    ubo_deposited = date_manipulations(ubo_deposited)
    ubo_redeemed = date_manipulations(ubo_redeemed)
    ubo_carbon = filter_pool_quantity(df_carbon_c3t, "UBO Quantity")

    # UBO Figures
    fig_deposited_over_time = deposited_over_time(ubo_deposited)
    fig_redeemed_over_time = redeemed_over_time(ubo_redeemed)
    zero_bridging_evt_text = "The UBO Pool is empty"
    fig_ubo_total_vintage = total_vintage(
        ubo_carbon, zero_bridging_evt_text)
    fig_ubo_total_map = map(ubo_carbon, zero_bridging_evt_text)
    fig_ubo_total_metho = methodology_volume(
        ubo_carbon, zero_bridging_evt_text)
    fig_ubo_total_project = project_volume(
        ubo_carbon, zero_bridging_evt_text)

    content_ubo = create_pool_content(
        "UBO", "Universal Base Offset", ubo_deposited, ubo_redeemed, None, ubo_carbon,
        fig_deposited_over_time, fig_redeemed_over_time, None, fig_ubo_total_vintage,
        fig_ubo_total_map, fig_ubo_total_metho, fig_ubo_total_project, KLIMA_RETIRED_NOTE,
        bridge_name="C3", bridge_ticker="C3T")

    cache.set("content_ubo", content_ubo)

    # --NBO---

    # Carbon pool filter
    nbo_deposited, nbo_redeemed = filter_carbon_pool(
        NBO_ADDRESS, df_deposited, df_redeemed
    )
    nbo_deposited = date_manipulations(nbo_deposited)
    nbo_redeemed = date_manipulations(nbo_redeemed)
    nbo_carbon = filter_pool_quantity(df_carbon_c3t, "NBO Quantity")

    # NBO Figures
    fig_deposited_over_time = deposited_over_time(nbo_deposited)
    fig_redeemed_over_time = redeemed_over_time(nbo_redeemed)
    zero_bridging_evt_text = "The NBO Pool is empty"
    fig_nbo_total_vintage = total_vintage(
        nbo_carbon, zero_bridging_evt_text)
    fig_nbo_total_map = map(nbo_carbon, zero_bridging_evt_text)
    fig_nbo_total_metho = methodology_volume(
        nbo_carbon, zero_bridging_evt_text)
    fig_nbo_total_project = project_volume(
        nbo_carbon, zero_bridging_evt_text)

    content_nbo = create_pool_content(
        "NBO", "Nature Base Offset", nbo_deposited, nbo_redeemed, None, nbo_carbon,
        fig_deposited_over_time, fig_redeemed_over_time, None, fig_nbo_total_vintage,
        fig_nbo_total_map, fig_nbo_total_metho, fig_nbo_total_project, KLIMA_RETIRED_NOTE,
        bridge_name="C3", bridge_ticker="C3T")

    cache.set("content_nbo", content_nbo)

    # ----Top Level Page---

    token_cg_dict['BCT']['Current Supply'] = bct_deposited["Quantity"].sum(
    ) - bct_redeemed["Quantity"].sum()
    token_cg_dict['NCT']['Current Supply'] = nct_deposited["Quantity"].sum(
    ) - nct_redeemed["Quantity"].sum()
    token_cg_dict['MCO2']['Current Supply'] = df_bridged_mco2["Quantity"].sum(
    ) - df_retired_mco2["Quantity"].sum()

    bridges_info_dict = {
        'Toucan': {'Dataframe': date_manipulations_verra(df_verra_toucan)},
        'Moss': {'Dataframe': df_bridged_mco2},
        'C3': {'Dataframe': date_manipulations_verra(df_verra_c3)}
    }

    retires_info_dict = {
        'Toucan': {'Dataframe': df_retired_tc},
        'Moss': {'Dataframe': df_retired_mco2},
        'C3': {'Dataframe': df_retired_c3t}
    }
    fig_bridges_pie_chart = bridges_pie_chart(bridges_info_dict)

    # ---offchain vs onchain---
    df_verra["Date"] = df_verra['Issuance Date']
    df_verra = date_manipulations_verra(df_verra)
    df_verra_retired = date_manipulations_verra(df_verra_retired)

    # Issued Figures
    fig_issued_over_time = deposited_over_time(df_verra)
    fig_tokenized_over_time = tokenized_volume(bridges_info_dict)
    fig_on_vs_off_vintage = on_vs_off_vintage(df_verra, bridges_info_dict)
    fig_on_vs_off_map = on_vs_off_map(df_verra, bridges_info_dict)
    fig_on_vs_off_project = on_vs_off_project(df_verra, bridges_info_dict)

    fig_on_vs_off_issued = [fig_issued_over_time, fig_tokenized_over_time,
                            fig_on_vs_off_vintage, fig_on_vs_off_map, fig_on_vs_off_project]
    titles_on_vs_off_issued = ["Cumulative Verra Registry Credits Issued Over Time",
                               "Cumulative Verra Registry Credits Tokenized Over Time",
                               "Credits Tokenized vs. Credits Issued by Vintage Start Dates",
                               "Credits Tokenized vs. Credits Issued by Origin",
                               "Credits Tokenized vs. Credits Issued by Project Type"]

    cache.set("fig_on_vs_off_issued", fig_on_vs_off_issued)
    cache.set("titles_on_vs_off_issued", titles_on_vs_off_issued)

    # Retired Figures
    fig_offchain_retired_over_time = deposited_over_time(df_verra_retired)
    fig_onchain_retired_over_time = tokenized_volume(retires_info_dict)
    fig_on_vs_off_vintage_retired = on_vs_off_vintage_retired(
        df_verra_retired, retires_info_dict)
    fig_on_vs_off_map_retired = on_vs_off_map_retired(
        df_verra_retired, retires_info_dict)
    fig_on_vs_off_project_retired = on_vs_off_project_retired(
        df_verra_retired, retires_info_dict)

    fig_on_vs_off_retired = [fig_offchain_retired_over_time, fig_onchain_retired_over_time,
                             fig_on_vs_off_vintage_retired, fig_on_vs_off_map_retired, fig_on_vs_off_project_retired]
    titles_on_vs_off_retired = ["Cumulative Off-Chain Verra Registry Credits Retired Over Time",
                                "Cumulative On-Chain Verra Registry Credits Retired Over Time",
                                "Off-Chain vs On-Chain Retired Credits by Vintage Start Dates",
                                "Off-Chain vs On-Chain Retired Credits by Origin",
                                "Off-Chain vs On-Chain Retired Credits by Project Type"]

    cache.set("fig_on_vs_off_retired", fig_on_vs_off_retired)
    cache.set("titles_on_vs_off_retired", titles_on_vs_off_retired)

    content_offchain_vs_onchain = create_offchain_vs_onchain_content(bridges_info_dict, retires_info_dict, df_verra,
                                                                     df_verra_retired, fig_bridges_pie_chart,
                                                                     verra_fallback_note)
    cache.set("content_offchain_vs_onchain", content_offchain_vs_onchain)

    # --- onchain carbon pool comparison ---
    fig_historical_prices = historical_prices(token_cg_dict, df_prices)
    content_onchain_pool_comp = create_onchain_pool_comp_content(
        token_cg_dict, df_prices, fig_historical_prices)
    cache.set("content_onchain_pool_comp", content_onchain_pool_comp)

    sidebar_toggle = dbc.Row(
        [
            dbc.Col(
                html.Button(
                    html.Span('menu', className="material-icons"),
                    className="navbar-toggler",
                    id="toggle",
                ),
                width="auto", align="center",
            ),
        ]
    )

    sidebar_header = [
        html.A([
            html.Img(src='assets/KlimaDAO-Wordmark-2.png',
                     className="klima-logo")
        ], href='https://www.klimadao.finance/',
            style={"padding": "0px"}),
        html.Hr(),
        html.H3("Tokenized Carbon Dashboards Beta",
                style={'textAlign': 'start'}, className="dashboard-title"),
        html.Hr(style={'margin-bottom': '1.5rem'}),
    ]

    sidebar = html.Div(
        [
            dbc.Nav(
                sidebar_header +
                [
                    html.H4("Top Level Summary", style={
                        'textAlign': 'left'}),
                    dbc.NavLink([
                        html.Div(
                            html.Span(
                                'link', className="material-icons"),
                            className='icon-container'),
                        html.Span(
                            'Off-Chain vs. On-Chain Carbon Market',
                            className='icon-title')
                    ], href="/", active="exact",
                    ),

                    dbc.NavLink([
                        html.Div(
                            html.Span(
                                'balance', className="material-icons"),
                            className='icon-container'),
                        html.Span(
                            "On-Chain Carbon Pools",
                            className='icon-title')
                    ], href="/CarbonPools", active="exact",
                    ),
                    html.Hr(style={"margin-top": "1.5rem"}),
                    html.A(html.H4("C3", style={
                        'textAlign': 'left'}),
                        href='https://www.c3.app/'),
                    dbc.NavLink([
                        html.Div(
                            html.Img(src='assets/C3_Logo_Cloud.png',
                                     className="moss-logo"),
                            className='icon-container'),
                        html.Span(
                            "C3T Overview")
                    ], href="/C3T", active="exact"
                    ),
                    dbc.NavLink([
                        html.Div(
                            html.Img(src='assets/C3-UBO-Logo.png',
                                     className="image-icons"),
                            className='icon-container'),
                        html.Span(
                            "UBO Pool")
                    ], href="/UBO", active="exact",
                    ),
                    dbc.NavLink([
                        html.Div(
                            html.Img(src='assets/C3-NBO-Logo.png',
                                     className="image-icons"),
                            className='icon-container'),
                        html.Span(
                            "NBO Pool")
                    ], href="/NBO", active="exact",
                    ),
                    html.Hr(style={"margin-top": "1.5rem"}),
                    html.A(html.H4("Moss", style={
                        'textAlign': 'left'}),
                        href='https://mco2token.moss.earth/'),
                    dbc.NavLink([
                        html.Div(
                            html.Img(src='assets/MCO2-Logo.png',
                                     className="moss-logo"),
                            className='icon-container'),
                        html.Span(
                            "MCO2 Overview")
                    ], href="/MCO2", active="exact",
                    ),
                    html.Hr(style={"margin-top": "1.5rem"}),
                    html.A(html.H4("Toucan", style={
                        'textAlign': 'left'}),
                        href='https://toucan.earth/'),
                    dbc.NavLink([
                        html.Div(
                            html.Img(src='assets/TCO2-Logo.png',
                                     className="image-icons"),
                            className='icon-container'),
                        html.Span(
                            "TCO2 Overview")
                    ], href="/TCO2", active="exact"
                    ),
                    dbc.NavLink([
                        html.Div(
                            html.Img(src='assets/BCT-Logo.png',
                                     className="moss-logo"),
                            className='icon-container'),
                        html.Span(
                            "BCT Pool")
                    ], href="/BCT", active="exact",
                    ),
                    dbc.NavLink([
                        html.Div(
                            html.Img(src='assets/NCT-Logo.png',
                                     className="moss-logo"),
                            className='icon-container'),
                        html.Span(
                            "NCT Pool")
                    ], href="/NCT", active="exact",
                    ),
                    html.Hr(style={"margin-top": "3rem"}),
                ],
                vertical=True,
                pills=True,
                style={'gap': '0.5rem'}
            )],
        className="sidebar",
    )

    sidebar_mobile = html.Div(
        [
            dbc.Offcanvas([
                dbc.Nav(sidebar_header +
                        [
                            html.H4("Top Level Summary", style={
                                'textAlign': 'left'}),
                            dbc.NavLink([
                                html.Div(
                                    html.Span(
                                        'link', className="material-icons"),
                                    className='icon-container'),
                                html.Span(
                                    'Off-Chain vs. On-Chain Carbon Market',
                                    className='icon-title')
                            ], href="/", active="exact",
                                id="button-off_vs_on_chain", n_clicks=0,
                            ),

                            dbc.NavLink([
                                html.Div(
                                    html.Span(
                                        'balance', className="material-icons"),
                                    className='icon-container'),
                                html.Span(
                                    "On-Chain Carbon Pools",
                                    className='icon-title')
                            ], href="/CarbonPools", active="exact",
                                id="button-onchain_pool_comp", n_clicks=0,
                            ),
                            html.Hr(style={"margin-top": "1.5rem"}),
                            html.A(html.H4("C3", style={
                                'textAlign': 'left'}),
                                href='https://www.c3.app/'),
                            dbc.NavLink([
                                html.Div(
                                    html.Img(src='assets/C3_Logo_Cloud.png',
                                             className="moss-logo"),
                                    className='icon-container'),
                                html.Span(
                                    "C3T Overview")
                            ], href="/C3T", active="exact",
                                id="button-c3t", n_clicks=0),
                            dbc.NavLink([
                                html.Div(
                                    html.Img(src='assets/C3-UBO-Logo.png',
                                             className="image-icons"),
                                    className='icon-container'),
                                html.Span(
                                    "UBO Pool")
                            ], href="/UBO", active="exact",
                                id="button-ubo", n_clicks=0
                            ),
                            dbc.NavLink([
                                html.Div(
                                    html.Img(src='assets/C3-NBO-Logo.png',
                                             className="image-icons"),
                                    className='icon-container'),
                                html.Span(
                                    "NBO Pool")
                            ], href="/NBO", active="exact",
                                id="button-nbo", n_clicks=0
                            ),
                            html.Hr(style={"margin-top": "1.5rem"}),
                            html.A(html.H4("Moss", style={
                                'textAlign': 'left'}),
                                href='https://mco2token.moss.earth/'),
                            dbc.NavLink([
                                html.Div(
                                    html.Img(src='assets/MCO2-Logo.png',
                                             className="moss-logo"),
                                    className='icon-container'),
                                html.Span(
                                    "MCO2 Overview")
                            ], href="/MCO2", active="exact",
                                id="button-mco2", n_clicks=0),
                            html.Hr(style={"margin-top": "1.5rem"}),
                            html.A(html.H4("Toucan", style={
                                'textAlign': 'left'}),
                                href='https://toucan.earth/'),
                            dbc.NavLink([
                                html.Div(
                                    html.Img(src='assets/TCO2-Logo.png',
                                             className="image-icons"),
                                    className='icon-container'),
                                html.Span(
                                    "TCO2 Overview")
                            ], href="/TCO2", active="exact", id="button-tco2", n_clicks=0
                            ),
                            dbc.NavLink([
                                html.Div(
                                    html.Img(src='assets/BCT-Logo.png',
                                             className="moss-logo"),
                                    className='icon-container'),
                                html.Span(
                                    "BCT Pool")
                            ], href="/BCT", active="exact",
                                id="button-bct", n_clicks=0
                            ),
                            dbc.NavLink([
                                html.Div(
                                    html.Img(src='assets/NCT-Logo.png',
                                             className="moss-logo"),
                                    className='icon-container'),
                                html.Span(
                                    "NCT Pool")
                            ], href="/NCT", active="exact",
                                id="button-nct", n_clicks=0
                            ),
                            html.Hr(style={"margin-top": "3rem"}),
                        ],
                        vertical=True,
                        pills=True,
                        style={'gap': '0.5rem'}
                        )],
                id="collapse",
                className="collapse",
                is_open=False,
            ),
        ],
        className="sidebar_mobile",
    )

    content = html.Div([dbc.Row([
        dbc.Col(sidebar_toggle, width=3,
                style={"padding": "0px"}),
        dbc.Col(),
        dbc.Col(html.H6(f"Last Updated: {curr_time_str} UTC",
                        id="lastupdated_indictor"), width=6,
                style={"padding": "0px"}),
    ], className="toggler-row"),
        sidebar_mobile,
        html.Div(id="page-content", children=[],
                 style={'padding-top': '5px'},
                 )], id='static-content')

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
def update_output_div_tc(summary_type, TCO2_type):
    if summary_type == 'Last 7 Days Performance':
        if TCO2_type == 'Bridged':
            fig_seven_day = cache.get("fig_seven_day_tc")
            return "Last 7 Days Performance", fig_seven_day[0], fig_seven_day[1], fig_seven_day[2], \
                fig_seven_day[3], fig_seven_day[4]
        elif TCO2_type == 'Retired':
            fig_seven_day_retired = cache.get("fig_seven_day_retired_tc")
            return "Last 7 Days Performance", fig_seven_day_retired[0], fig_seven_day_retired[1], \
                fig_seven_day_retired[2], fig_seven_day_retired[3], fig_seven_day_retired[4]

    elif summary_type == 'Last 30 Days Performance':
        if TCO2_type == 'Bridged':
            fig_thirty_day = cache.get("fig_thirty_day_tc")
            return "Last 30 Days Performance", fig_thirty_day[0], fig_thirty_day[1], fig_thirty_day[2], \
                fig_thirty_day[3], fig_thirty_day[4]
        elif TCO2_type == 'Retired':
            fig_thirty_day_retired = cache.get("fig_thirty_day_retired_tc")
            return "Last 30 Days Performance", fig_thirty_day_retired[0], fig_thirty_day_retired[1], \
                fig_thirty_day_retired[2], fig_thirty_day_retired[3], fig_thirty_day_retired[4]

    elif summary_type == 'Lifetime Performance':
        if TCO2_type == 'Bridged':
            fig_total = cache.get("fig_total_tc")
            return "Lifetime Performance", fig_total[0], fig_total[1], fig_total[2],\
                fig_total[3], fig_total[4]
        elif TCO2_type == 'Retired':
            fig_total_retired = cache.get("fig_total_retired_tc")
            return "Lifetime Performance", fig_total_retired[0], fig_total_retired[1], fig_total_retired[2],\
                fig_total_retired[3], fig_total_retired[4]


@callback(
    Output(component_id='Last X Days_c3t', component_property='children'),
    Output(component_id='volume plot_c3t', component_property='figure'),
    Output(component_id='vintage plot_c3t', component_property='figure'),
    Output(component_id='map_c3t', component_property='figure'),
    Output(component_id="methodology_c3t", component_property='figure'),
    Output(component_id="projects_c3t", component_property='figure'),
    Input(component_id='summary_type_c3t', component_property='value'),
    Input(component_id='bridged_or_retired_c3t', component_property='value')
)
def update_output_div_c3(summary_type, C3T_type):
    if summary_type == 'Last 7 Days Performance':
        if C3T_type == 'Bridged':
            fig_seven_day = cache.get("fig_seven_day_c3t")
            return "Last 7 Days Performance", fig_seven_day[0], fig_seven_day[1], fig_seven_day[2], \
                fig_seven_day[3], fig_seven_day[4]
        elif C3T_type == 'Retired':
            fig_seven_day_retired = cache.get("fig_seven_day_retired_c3t")
            return "Last 7 Days Performance", fig_seven_day_retired[0], fig_seven_day_retired[1], \
                fig_seven_day_retired[2], fig_seven_day_retired[3], fig_seven_day_retired[4]

    elif summary_type == 'Last 30 Days Performance':
        if C3T_type == 'Bridged':
            fig_thirty_day = cache.get("fig_thirty_day_c3t")
            return "Last 30 Days Performance", fig_thirty_day[0], fig_thirty_day[1], fig_thirty_day[2], \
                fig_thirty_day[3], fig_thirty_day[4]
        elif C3T_type == 'Retired':
            fig_thirty_day_retired = cache.get("fig_thirty_day_retired_c3t")
            return "Last 30 Days Performance", fig_thirty_day_retired[0], fig_thirty_day_retired[1], \
                fig_thirty_day_retired[2], fig_thirty_day_retired[3], fig_thirty_day_retired[4]

    elif summary_type == 'Lifetime Performance':
        if C3T_type == 'Bridged':
            fig_total = cache.get("fig_total_c3t")
            return "Lifetime Performance", fig_total[0], fig_total[1], fig_total[2],\
                fig_total[3], fig_total[4]
        elif C3T_type == 'Retired':
            fig_total_retired = cache.get("fig_total_retired_c3t")
            return "Lifetime Performance", fig_total_retired[0], fig_total_retired[1], fig_total_retired[2],\
                fig_total_retired[3], fig_total_retired[4]


@callback(
    Output(component_id='offchain-volume-title',
           component_property='children'),
    Output(component_id='onchain-volume-title', component_property='children'),
    Output(component_id='on_vs_off_vintage_title',
           component_property='children'),
    Output(component_id="on_vs_off_origin_title",
           component_property='children'),
    Output(component_id="on_vs_off_project_title",
           component_property='children'),
    Output(component_id='offchain-volume-plot', component_property='figure'),
    Output(component_id='onchain-volume-plot', component_property='figure'),
    Output(component_id='on_vs_off_vintage_plot', component_property='figure'),
    Output(component_id="on_vs_off_origin_plot", component_property='figure'),
    Output(component_id="on_vs_off_project_plot", component_property='figure'),
    Output(component_id='on_vs_off_vintage_footer',
           component_property='children'),
    Output(component_id='on_vs_off_origin_footer',
           component_property='children'),
    Output(component_id='on_vs_off_project_footer',
           component_property='children'),
    Input(component_id='issued_or_retired', component_property='value')
)
def update_output_on_vs_off(type):

    if type == 'Issued':
        titles_on_vs_off_issued = cache.get("titles_on_vs_off_issued")
        fig_on_vs_off_issued = cache.get("fig_on_vs_off_issued")
        return titles_on_vs_off_issued[0], titles_on_vs_off_issued[1], titles_on_vs_off_issued[2], \
            titles_on_vs_off_issued[3], titles_on_vs_off_issued[4], \
            fig_on_vs_off_issued[0], fig_on_vs_off_issued[1], fig_on_vs_off_issued[2], \
            fig_on_vs_off_issued[3], fig_on_vs_off_issued[4], None, None, None
    elif type == 'Retired':
        moss_note = 'Note: Project metadata of Moss Retired VCUs is unavailable'
        titles_on_vs_off_retired = cache.get("titles_on_vs_off_retired")
        fig_on_vs_off_retired = cache.get("fig_on_vs_off_retired")
        return titles_on_vs_off_retired[0], titles_on_vs_off_retired[1], \
            titles_on_vs_off_retired[2], titles_on_vs_off_retired[3], titles_on_vs_off_retired[4], \
            fig_on_vs_off_retired[0], fig_on_vs_off_retired[1], \
            fig_on_vs_off_retired[2], fig_on_vs_off_retired[3], fig_on_vs_off_retired[4], \
            moss_note, moss_note, moss_note


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
        content_offchain_vs_onchain = cache.get("content_offchain_vs_onchain")
        return content_offchain_vs_onchain

    elif pathname == "/CarbonPools":
        content_onchain_pool_comp = cache.get("content_onchain_pool_comp")
        return content_onchain_pool_comp

    elif pathname == "/TCO2":
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

    elif pathname == "/C3T":
        content_c3t = cache.get("content_c3t")
        return content_c3t

    elif pathname == "/UBO":
        content_ubo = cache.get("content_ubo")
        return content_ubo

    elif pathname == "/NBO":
        content_nbo = cache.get("content_nbo")
        return content_nbo

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
     Input("button-off_vs_on_chain", "n_clicks"),
     Input("button-onchain_pool_comp", "n_clicks"),
     Input("button-tco2", "n_clicks"),
     Input("button-bct", "n_clicks"),
     Input("button-nct", "n_clicks"),
     Input("button-mco2", "n_clicks"),
     Input("button-c3t", "n_clicks"),
     Input("button-ubo", "n_clicks"),
     Input("button-nbo", "n_clicks"), ],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, n_off_vs_on, n_all_carbon_pools, n_tco2, n_bct, n_nct, n_mco2, n_c3t,
                    n_ubo, n_nbo, is_open):
    if n or n_off_vs_on or n_all_carbon_pools or n_tco2 or n_bct or n_nct or n_mco2 or n_c3t or \
            n_ubo or n_nbo:
        return not is_open
    return is_open


# For Gunicorn to reference
server = app.server


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
