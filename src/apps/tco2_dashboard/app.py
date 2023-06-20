import dash_bootstrap_components as dbc
import dash
from datetime import datetime
from dash import html, Input, Output, callback, State
from dash import dcc
from .services import layout_cache as cache, services_slow_cache, services_fast_cache
import pandas as pd

from src.apps.tco2_dashboard.retirement_trends.retirement_trends_page \
    import create_content_retirement_trends, TYPE_POOL, TYPE_TOKEN, \
    TYPE_CHAIN, TYPE_BENEFICIARY, create_retirement_trend_inputs

from ...util import is_production, load_s3_data, debug
from src.apps.tco2_dashboard.carbon_supply import create_carbon_supply_content
from .figures import (
    sub_plots_vintage,
    sub_plots_volume,
    map,
    methodology_volume,
    project_volume,
    eligible_pool_pie_chart,
    pool_pie_chart,
    historical_prices,
    bridges_pie_chart,
    on_vs_off_vintage,
    on_vs_off_map,
    on_vs_off_project,
    tokenized_volume,
    on_vs_off_vintage_retired,
    on_vs_off_map_retired,
    on_vs_off_project_retired,
    # create_offchain_vs_onchain_figs,
    create_offchain_vs_onchain_fig,
    create_retirements_fig,
    total_carbon_supply_pie_chart,
)
from .figures_carbon_pool import (
    deposited_over_time,
    redeemed_over_time,
    retired_over_time,
)
from .offchain_vs_onchain import create_offchain_vs_onchain_content
from .homepage import create_homepage_content
from .onchain_pool_comp import create_onchain_pool_comp_content
from .tco2 import create_content_toucan
from .c3t import create_content_c3t
from .pool import create_pool_content
from .mco2 import create_content_moss
from .helpers import (
    date_manipulations,
    filter_pool_quantity,
    drop_duplicates,
    filter_carbon_pool,
    bridge_manipulations,
    mco2_verra_manipulations,
    verra_retired,
    date_manipulations_verra,
    off_vs_on_data,
    create_retirements_data,
    create_holders_data,
    merge_retirements_data_for_retirement_chart,
)
from .constants import (
    KLIMA_RETIRED_NOTE,
)

GOOGLE_API_ICONS = {
    "href": "https://fonts.googleapis.com/icon?family=Material+Icons|Material+Icons+Outlined|"
    "Material+Icons+Two+Tone|Material+Icons+Round|Material+Icons+Sharp",
    "rel": "stylesheet",
}
POPPINS_FONT = {
    "href": "https://fonts.googleapis.com/css2?family=Poppins:wght@100;400;500;600;800;900&display=swap",
    "rel": "stylesheet",
}
INTER_FONT = {
    "href": "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap",
    "rel": "stylesheet",
}
FONT_AWESOME_ICONS = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
)

# Configure plausible.io tracking script
external_scripts = (
    [
        {
            "src": "https://plausible.io/js/script.js",
            "data-domain": "carbon.klimadao.finance",
        }
    ]
    if is_production()
    else []
)

app = dash.Dash(
    __name__,
    title="KlimaDAO Digital Carbon Dashboard",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        GOOGLE_API_ICONS,
        INTER_FONT,
        POPPINS_FONT,
        dbc.icons.FONT_AWESOME,
        FONT_AWESOME_ICONS,
    ],
    external_scripts=external_scripts,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"property": "og:type", "content": "website"},
        {"property": "og:site_name", "content": "KlimaDAO Carbon Dashboards"},
        {"property": "og:title", "content": "State of Digital Carbon"},
        {
            "property": "og:description",
            "content": """
            Data visualizations, analytics and detailed drilldowns
            into the state of the on-chain carbon markets in the Ethereum ecosystem.
            """,
        },
        {
            "property": "og:image",
            "content": "https://www.klimadao.finance/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fdk34t4vc%2Fproduction%2F0be338e1930c5bf36101feaa7669c8330057779a-2156x1080.png&w=1920&q=75",  # noqa: E501
        },
        {"name": "twitter:card", "content": "summary_large_image"},
        {"name": "twitter:site", "content": "@discord"},
        {"name": "twitter:creator", "content": "@KlimaDAO"},
    ],
)


# Add GTM for analytics via index_string
gtm_head_section = (
    """
        <!-- Google Tag Manager -->
        <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','GTM-KWFJ9R2');</script>
        <!-- End Google Tag Manager -->
"""
    if is_production()
    else ""
)

gtm_body_section = (
    """
        <!-- Google Tag Manager (noscript) -->
        <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-KWFJ9R2"
        height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
        <!-- End Google Tag Manager (noscript) -->
"""
    if is_production()
    else ""
)

app.index_string = (
    """
<!DOCTYPE html>
<html>
    <head>
"""
    + gtm_head_section
    + """
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
"""
    + gtm_body_section
    + """
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""
)


cache.init_app(app.server)
services_slow_cache.init_app(app.server)
services_fast_cache.init_app(app.server)


@cache.memoize()
def get_s3_data(slug: str) -> pd.DataFrame:
    debug(f"get s3 data: {slug}")
    return load_s3_data(slug)


@cache.memoize()
def generate_layout():
    debug("Render: generate_layout")
    curr_time_str = datetime.utcnow().strftime("%b %d %Y %H:%M:%S UTC")

    df = get_s3_data("polygon_bridged_offsets")
    df_retired = get_s3_data("polygon_retired_offsets")

    df_deposited = get_s3_data("raw_polygon_pools_deposited_offsets")
    df_redeemed = get_s3_data("raw_polygon_pools_redeemed_offsets")

    df_pool_retired = get_s3_data("raw_polygon_pools_retired_offsets")

    df_bridged_mco2 = get_s3_data("eth_moss_bridged_offsets")
    df_retired_mco2 = get_s3_data("eth_retired_offsets")
    df_retired_mco2_info = get_s3_data("raw_eth_moss_retired_offsets")
    df_verra = get_s3_data("verra_data")
    df_verra_toucan = df_verra.query("Toucan")
    df_verra_c3 = df_verra.query("C3")
    df_verra_retired = verra_retired(df_verra)
    verra_fallback_note = ""

    tokens_dict = (
        get_s3_data("tokens_data")
        .set_index("Name")
        .transpose()
        .to_dict(orient='dict')
    )
    BCT_ADDRESS = tokens_dict["BCT"]["address"]
    NCT_ADDRESS = tokens_dict["NCT"]["address"]
    UBO_ADDRESS = tokens_dict["UBO"]["address"]
    NBO_ADDRESS = tokens_dict["NBO"]["address"]

    current_price_only_token_list = []
    price_source = "Subgraph"
    df_prices = get_s3_data("raw_assets_prices")
    df_holdings = get_s3_data("raw_offsets_holders_data")

    # -----TCO2_Figures----
    # Bridge manipulations
    df_tc = bridge_manipulations(df, "Toucan")
    df_retired_tc = bridge_manipulations(df_retired, "Toucan")
    # datetime manipulations
    df_tc = date_manipulations(df_tc)
    df_retired_tc = date_manipulations(df_retired_tc)
    # Blacklist manipulations
    # df = black_list_manipulations(df)
    # df_retired = black_list_manipulations(df_retired)

    # 7 day and 30 day subsets
    # drop duplicates data for Carbon Pool calculations
    df_carbon_tc = drop_duplicates(df_tc)
    cache.set("df_carbon_tc", df_carbon_tc)

    # Figures
    # 7-day-performance
    fig_seven_day_volume_tc = sub_plots_volume("Toucan", None, "bridged", 7)
    fig_seven_day_volume_retired_tc = sub_plots_volume("Toucan", None, "retired", 7)
    fig_seven_day_vintage_tc = sub_plots_vintage("Toucan", None, "bridged", 7)
    fig_seven_day_vintage_retired_tc = sub_plots_vintage("Toucan", None, "retired", 7)
    fig_seven_day_map_tc = map("Toucan", None, "bridged", 7)
    fig_seven_day_map_retired_tc = map("Toucan", None, "retired", 7)
    fig_seven_day_metho_tc = methodology_volume("Toucan", None, "bridged", 7)
    fig_seven_day_metho_retired_tc = methodology_volume("Toucan", None, "retired", 7)
    fig_seven_day_project_tc = project_volume("Toucan", None, "bridged", 7)
    fig_seven_day_project_retired_tc = project_volume("Toucan", None, "retired", 7)

    # 30-day-performance
    fig_thirty_day_volume_tc = sub_plots_volume("Toucan", None, "bridged", 30)
    fig_thirty_day_volume_retired_tc = sub_plots_volume("Toucan", None, "retired", 30)
    fig_thirty_day_vintage_tc = sub_plots_vintage("Toucan", None, "bridged", 30)
    fig_thirty_day_vintage_retired_tc = sub_plots_vintage("Toucan", None, "retired", 30)
    fig_thirty_day_map_tc = map("Toucan", None, "bridged", 30)
    fig_thirty_day_map_retired_tc = map("Toucan", None, "retired", 30)
    fig_thirty_day_metho_tc = methodology_volume("Toucan", None, "bridged", 30)
    fig_thirty_day_metho_retired_tc = methodology_volume("Toucan", None, "retired", 30)
    fig_thirty_day_project_tc = project_volume("Toucan", None, "bridged", 30)
    fig_thirty_day_project_retired_tc = project_volume("Toucan", None, "retired", 30)

    # Content carbon supply
    polygon_carbon_metrics_df = get_s3_data("raw_polygon_carbon_metrics")
    eth_carbon_metrics_df = get_s3_data("raw_eth_carbon_metrics")
    celo_carbon_metrics_df = get_s3_data("raw_celo_carbon_metrics")
    fig_total_carbon_supply_pie_chart = total_carbon_supply_pie_chart()
    content_carbon_supply = create_carbon_supply_content(
        polygon_carbon_metrics_df,
        eth_carbon_metrics_df,
        celo_carbon_metrics_df,
        fig_total_carbon_supply_pie_chart,
    )

    cache.set("content_carbon_supply", content_carbon_supply)

    # Total
    fig_total_volume_tc = sub_plots_volume("Toucan", None, "bridged")
    fig_total_volume_retired_tc = sub_plots_volume("Toucan", None, "retired")
    fig_total_vintage_tc = sub_plots_vintage("Toucan", None, "bridged")
    fig_total_vintage_retired_tc = sub_plots_vintage("Toucan", None, "retired")
    fig_total_map_tc = map("Toucan", None, "bridged")
    fig_total_map_retired_tc = map("Toucan", None, "retired")
    fig_total_metho_tc = methodology_volume("Toucan", None, "bridged")
    fig_total_metho_retired_tc = methodology_volume("Toucan", None, "retired")
    fig_total_project_tc = project_volume("Toucan", None, "bridged")
    fig_total_project_retired_tc = project_volume("Toucan", None, "retired")

    fig_pool_pie_chart_tc = pool_pie_chart(df_carbon_tc, ["BCT", "NCT"])
    content_tco2 = create_content_toucan(df_tc, df_retired_tc, fig_pool_pie_chart_tc)

    fig_seven_day_tc = [
        fig_seven_day_volume_tc,
        fig_seven_day_vintage_tc,
        fig_seven_day_map_tc,
        fig_seven_day_metho_tc,
        fig_seven_day_project_tc,
    ]
    fig_seven_day_retired_tc = [
        fig_seven_day_volume_retired_tc,
        fig_seven_day_vintage_retired_tc,
        fig_seven_day_map_retired_tc,
        fig_seven_day_metho_retired_tc,
        fig_seven_day_project_retired_tc,
    ]
    fig_thirty_day_tc = [
        fig_thirty_day_volume_tc,
        fig_thirty_day_vintage_tc,
        fig_thirty_day_map_tc,
        fig_thirty_day_metho_tc,
        fig_thirty_day_project_tc,
    ]
    fig_thirty_day_retired_tc = [
        fig_thirty_day_volume_retired_tc,
        fig_thirty_day_vintage_retired_tc,
        fig_thirty_day_map_retired_tc,
        fig_thirty_day_metho_retired_tc,
        fig_thirty_day_project_retired_tc,
    ]
    fig_total_tc = [
        fig_total_volume_tc,
        fig_total_vintage_tc,
        fig_total_map_tc,
        fig_total_metho_tc,
        fig_total_project_tc,
    ]
    fig_total_retired_tc = [
        fig_total_volume_retired_tc,
        fig_total_vintage_retired_tc,
        fig_total_map_retired_tc,
        fig_total_metho_retired_tc,
        fig_total_project_retired_tc,
    ]

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
    # 7 day and 30 day subsets
    # drop duplicates data for Carbon Pool calculations
    df_carbon_c3t = drop_duplicates(df_c3t)
    cache.set("df_carbon_c3t", df_carbon_c3t)

    # Figures
    # 7-day-performance
    fig_seven_day_volume_c3t = sub_plots_volume("C3", None, "bridged", 7)
    fig_seven_day_volume_retired_c3t = sub_plots_volume("C3", None, "retired", 7)
    fig_seven_day_vintage_c3t = sub_plots_vintage("C3", None, "bridged", 7)
    fig_seven_day_vintage_retired_c3t = sub_plots_vintage("C3", None, "retired", 7)
    fig_seven_day_map_c3t = map("C3", None, "bridged", 7)
    fig_seven_day_map_retired_c3t = map("C3", None, "retired", 7)
    fig_seven_day_metho_c3t = methodology_volume("C3", None, "bridged", 7)
    fig_seven_day_metho_retired_c3t = methodology_volume("C3", None, "retired", 7)
    fig_seven_day_project_c3t = project_volume("C3", None, "bridged", 7)
    fig_seven_day_project_retired_c3t = project_volume("C3", None, "retired", 7)

    # 30-day-performance
    fig_thirty_day_volume_c3t = sub_plots_volume("C3", None, "bridged", 30)
    fig_thirty_day_volume_retired_c3t = sub_plots_volume("C3", None, "retired", 30)
    fig_thirty_day_vintage_c3t = sub_plots_vintage("C3", None, "bridged", 30)
    fig_thirty_day_vintage_retired_c3t = sub_plots_vintage("C3", None, "retired", 30)
    fig_thirty_day_map_c3t = map("C3", None, "bridged", 30)
    fig_thirty_day_map_retired_c3t = map("C3", None, "retired", 30)
    fig_thirty_day_metho_c3t = methodology_volume("C3", None, "bridged", 30)
    fig_thirty_day_metho_retired_c3t = methodology_volume("C3", None, "retired", 30)
    fig_thirty_day_project_c3t = project_volume("C3", None, "bridged", 30)
    fig_thirty_day_project_retired_c3t = project_volume("C3", None, "retired", 30)

    # Total
    fig_total_volume_c3t = sub_plots_volume("C3", None, "bridged")
    fig_total_volume_retired_c3t = sub_plots_volume("C3", None, "retired")
    fig_total_vintage_c3t = sub_plots_vintage("C3", None, "bridged")
    fig_total_vintage_retired_c3t = sub_plots_vintage("C3", None, "retired")
    fig_total_map_c3t = map("C3", None, "bridged")
    fig_total_map_retired_c3t = map("C3", None, "retired")
    fig_total_metho_c3t = methodology_volume("C3", None, "bridged")
    fig_total_metho_retired_c3t = methodology_volume("C3", None, "retired")
    fig_total_project_c3t = project_volume("C3", None, "bridged")
    fig_total_project_retired_c3t = project_volume("C3", None, "retired")
    fig_pool_pie_chart_c3t = pool_pie_chart(df_carbon_c3t, ["UBO", "NBO"])

    content_c3t = create_content_c3t(df_c3t, df_retired_c3t, fig_pool_pie_chart_c3t)

    fig_seven_day_c3t = [
        fig_seven_day_volume_c3t,
        fig_seven_day_vintage_c3t,
        fig_seven_day_map_c3t,
        fig_seven_day_metho_c3t,
        fig_seven_day_project_c3t,
    ]
    fig_seven_day_retired_c3t = [
        fig_seven_day_volume_retired_c3t,
        fig_seven_day_vintage_retired_c3t,
        fig_seven_day_map_retired_c3t,
        fig_seven_day_metho_retired_c3t,
        fig_seven_day_project_retired_c3t,
    ]
    fig_thirty_day_c3t = [
        fig_thirty_day_volume_c3t,
        fig_thirty_day_vintage_c3t,
        fig_thirty_day_map_c3t,
        fig_thirty_day_metho_c3t,
        fig_thirty_day_project_c3t,
    ]
    fig_thirty_day_retired_c3t = [
        fig_thirty_day_volume_retired_c3t,
        fig_thirty_day_vintage_retired_c3t,
        fig_thirty_day_map_retired_c3t,
        fig_thirty_day_metho_retired_c3t,
        fig_thirty_day_project_retired_c3t,
    ]
    fig_total_c3t = [
        fig_total_volume_c3t,
        fig_total_vintage_c3t,
        fig_total_map_c3t,
        fig_total_metho_c3t,
        fig_total_project_c3t,
    ]
    fig_total_retired_c3t = [
        fig_total_volume_retired_c3t,
        fig_total_vintage_retired_c3t,
        fig_total_map_retired_c3t,
        fig_total_metho_retired_c3t,
        fig_total_project_retired_c3t,
    ]

    cache.set("fig_seven_day_c3t", fig_seven_day_c3t)
    cache.set("fig_seven_day_retired_c3t", fig_seven_day_retired_c3t)
    cache.set("fig_thirty_day_c3t", fig_thirty_day_c3t)
    cache.set("fig_thirty_day_retired_c3t", fig_thirty_day_retired_c3t)
    cache.set("fig_total_c3t", fig_total_c3t)
    cache.set("fig_total_retired_c3t", fig_total_retired_c3t)
    cache.set("content_c3t", content_c3t)

    # --MCO2 Figures--

    df_retired_mco2 = bridge_manipulations(df_retired_mco2, "Moss")
    df_bridged_mco2 = date_manipulations_verra(df_bridged_mco2)
    df_retired_mco2 = date_manipulations(df_retired_mco2)

    fig_mco2_total_volume = deposited_over_time(df_bridged_mco2)
    fig_mco2_total_vintage = sub_plots_vintage("Moss", None, "bridged")
    fig_mco2_total_map = map("Moss", None, "bridged")
    fig_mco2_total_metho = methodology_volume("Moss", None, "bridged")
    fig_mco2_total_project = project_volume("Moss", None, "bridged")
    df_bridged_mco2_summary = mco2_verra_manipulations(df_bridged_mco2)
    mco2_carbon = (
        df_bridged_mco2_summary.groupby(
            ["Project ID", "Country", "Methodology", "Project Type", "Name", "Vintage"]
        )["Quantity"]
        .sum()
        .to_frame()
        .reset_index()
    )
    mco2_carbon = mco2_carbon[
        [
            "Project ID",
            "Quantity",
            "Vintage",
            "Country",
            "Project Type",
            "Methodology",
            "Name",
        ]
    ]
    content_mco2 = create_content_moss(
        df_bridged_mco2_summary,
        df_retired_mco2,
        mco2_carbon,
        fig_mco2_total_volume,
        fig_mco2_total_vintage,
        fig_mco2_total_map,
        fig_mco2_total_metho,
        fig_mco2_total_project,
    )

    cache.set("content_mco2", content_mco2)
    cache.set("mco2_carbon", mco2_carbon)

    # --Carbon Pool Figures---

    # Blacklist manipulations
    # df_deposited = black_list_manipulations(df_deposited)
    # df_redeemed = black_list_manipulations(df_redeemed)

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
    fig_retired_over_time = retired_over_time(BCT_ADDRESS, "BCT", df_pool_retired)
    fig_bct_total_vintage = sub_plots_vintage("Toucan", "BCT", "bridged")
    fig_bct_total_map = map("Toucan", "BCT", "bridged")
    fig_bct_total_metho = methodology_volume("Toucan", "BCT", "bridged")
    fig_bct_total_project = project_volume("Toucan", "BCT", "bridged")

    content_bct = create_pool_content(
        "BCT",
        "Base Carbon Tonne",
        bct_deposited,
        bct_redeemed,
        bct_retired,
        bct_carbon,
        fig_deposited_over_time,
        fig_redeemed_over_time,
        fig_retired_over_time,
        fig_bct_total_vintage,
        fig_bct_total_map,
        fig_bct_total_metho,
        fig_bct_total_project,
        KLIMA_RETIRED_NOTE,
    )

    cache.set("content_bct", content_bct)
    cache.set("bct_carbon", bct_carbon)

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
    fig_retired_over_time = retired_over_time(NCT_ADDRESS, "NCT", df_pool_retired)
    fig_nct_total_vintage = sub_plots_vintage("Toucan", "NCT", "bridged")
    fig_nct_total_map = map("Toucan", "NCT", "bridged")
    fig_nct_total_metho = methodology_volume("Toucan", "NCT", "bridged")
    fig_nct_total_project = project_volume("Toucan", "NCT", "bridged")

    content_nct = create_pool_content(
        "NCT",
        "Nature Carbon Tonne",
        nct_deposited,
        nct_redeemed,
        nct_retired,
        nct_carbon,
        fig_deposited_over_time,
        fig_redeemed_over_time,
        fig_retired_over_time,
        fig_nct_total_vintage,
        fig_nct_total_map,
        fig_nct_total_metho,
        fig_nct_total_project,
        KLIMA_RETIRED_NOTE,
    )

    cache.set("content_nct", content_nct)
    cache.set("nct_carbon", nct_carbon)

    # --UBO---

    # Carbon pool filter
    df_carbon_c3t["Project ID"] = df_carbon_c3t["Project ID"]
    ubo_deposited, ubo_redeemed = filter_carbon_pool(
        UBO_ADDRESS, df_deposited, df_redeemed
    )
    ubo_deposited = date_manipulations(ubo_deposited)
    ubo_redeemed = date_manipulations(ubo_redeemed)
    ubo_carbon = filter_pool_quantity(df_carbon_c3t, "UBO Quantity")

    # UBO Figures
    fig_deposited_over_time = deposited_over_time(ubo_deposited)
    fig_redeemed_over_time = redeemed_over_time(ubo_redeemed)
    fig_ubo_total_vintage = sub_plots_vintage("Toucan", "UBO", "bridged")
    fig_ubo_total_map = map("C3", "UBO", "bridged")
    fig_ubo_total_metho = methodology_volume("C3", "UBO", "bridged")
    fig_ubo_total_project = project_volume("C3", "UBO", "bridged")

    content_ubo = create_pool_content(
        "UBO",
        "Universal Base Offset",
        ubo_deposited,
        ubo_redeemed,
        None,
        ubo_carbon,
        fig_deposited_over_time,
        fig_redeemed_over_time,
        None,
        fig_ubo_total_vintage,
        fig_ubo_total_map,
        fig_ubo_total_metho,
        fig_ubo_total_project,
        KLIMA_RETIRED_NOTE,
        bridge_name="C3",
        bridge_ticker="C3T",
    )

    cache.set("content_ubo", content_ubo)
    cache.set("ubo_carbon", ubo_carbon)

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
    fig_nbo_total_vintage = sub_plots_vintage("C3", "NBO", "bridged")
    fig_nbo_total_map = map("C3", "NBO", "bridged")
    fig_nbo_total_metho = methodology_volume("C3", "NBO", "bridged")
    fig_nbo_total_project = project_volume("C3", "NBO", "bridged")

    content_nbo = create_pool_content(
        "NBO",
        "Nature Base Offset",
        nbo_deposited,
        nbo_redeemed,
        None,
        nbo_carbon,
        fig_deposited_over_time,
        fig_redeemed_over_time,
        None,
        fig_nbo_total_vintage,
        fig_nbo_total_map,
        fig_nbo_total_metho,
        fig_nbo_total_project,
        KLIMA_RETIRED_NOTE,
        bridge_name="C3",
        bridge_ticker="C3T",
    )

    cache.set("content_nbo", content_nbo)
    cache.set("nbo_carbon", nbo_carbon)

    # ----Top Level Page---

    bridges_info_dict = {
        "Toucan": {"Dataframe": date_manipulations_verra(df_verra_toucan)},
        "Moss": {"Dataframe": df_bridged_mco2},
        "C3": {"Dataframe": date_manipulations_verra(df_verra_c3)},
    }

    retires_info_dict = {
        "Toucan": {"Dataframe": df_retired_tc},
        "Moss": {"Dataframe": df_retired_mco2},
        "C3": {"Dataframe": df_retired_c3t},
    }
    fig_bridges_pie_chart = bridges_pie_chart(bridges_info_dict)

    # ---offchain vs onchain---
    df_verra["Date"] = df_verra["Issuance Date"]
    df_verra = date_manipulations_verra(df_verra)
    df_verra_retired = date_manipulations_verra(df_verra_retired)

    # Issued Figures
    fig_issued_over_time = deposited_over_time(df_verra)
    fig_tokenized_over_time = tokenized_volume(bridges_info_dict)
    fig_on_vs_off_vintage = on_vs_off_vintage(df_verra, bridges_info_dict)
    fig_on_vs_off_map = on_vs_off_map(df_verra, bridges_info_dict)
    fig_on_vs_off_project = on_vs_off_project(df_verra, bridges_info_dict)

    fig_on_vs_off_issued = [
        fig_issued_over_time,
        fig_tokenized_over_time,
        fig_on_vs_off_vintage,
        fig_on_vs_off_map,
        fig_on_vs_off_project,
    ]
    titles_on_vs_off_issued = [
        "Cumulative Verra Registry Credits Issued Over Time",
        "Cumulative Verra Registry Credits Tokenized Over Time",
        "Credits Tokenized vs. Credits Issued by Vintage Start Dates",
        "Credits Tokenized vs. Credits Issued by Origin",
        "Credits Tokenized vs. Credits Issued by Project Type",
    ]

    cache.set("fig_on_vs_off_issued", fig_on_vs_off_issued)
    cache.set("titles_on_vs_off_issued", titles_on_vs_off_issued)

    # Retired Figures
    fig_offchain_retired_over_time = deposited_over_time(df_verra_retired)
    fig_onchain_retired_over_time = tokenized_volume(retires_info_dict)
    fig_on_vs_off_vintage_retired = on_vs_off_vintage_retired(
        df_verra_retired, retires_info_dict
    )
    fig_on_vs_off_map_retired = on_vs_off_map_retired(
        df_verra_retired, retires_info_dict
    )
    fig_on_vs_off_project_retired = on_vs_off_project_retired(
        df_verra_retired, retires_info_dict
    )

    fig_on_vs_off_retired = [
        fig_offchain_retired_over_time,
        fig_onchain_retired_over_time,
        fig_on_vs_off_vintage_retired,
        fig_on_vs_off_map_retired,
        fig_on_vs_off_project_retired,
    ]
    titles_on_vs_off_retired = [
        "Cumulative Off-Chain Verra Registry Credits Retired Over Time",
        "Cumulative On-Chain Verra Registry Credits Retired Over Time",
        "Off-Chain vs On-Chain Retired Credits by Vintage Start Dates",
        "Off-Chain vs On-Chain Retired Credits by Origin",
        "Off-Chain vs On-Chain Retired Credits by Project Type",
    ]

    cache.set("fig_on_vs_off_retired", fig_on_vs_off_retired)
    cache.set("titles_on_vs_off_retired", titles_on_vs_off_retired)

    content_offchain_vs_onchain = create_offchain_vs_onchain_content(
        bridges_info_dict,
        retires_info_dict,
        df_verra,
        df_verra_retired,
        fig_bridges_pie_chart,
        verra_fallback_note,
    )
    cache.set("content_offchain_vs_onchain", content_offchain_vs_onchain)

    # Content Retirement trends
    klima_retirements_df = get_s3_data("raw_polygon_klima_retirements")
    daily_agg_klima_retirements_df = get_s3_data("raw_polygon_klima_retirements_daily")

    retirement_trend_inputs = create_retirement_trend_inputs(
        polygon_carbon_metrics_df,
        eth_carbon_metrics_df,
        klima_retirements_df,
        daily_agg_klima_retirements_df,
        df_verra_retired,
        df_verra,
        bridges_info_dict,
        verra_fallback_note
    )

    content_token_retirement_trends = create_content_retirement_trends(
        TYPE_TOKEN,
        retirement_trend_inputs
    )
    cache.set("content_token_retirement_trends",
              content_token_retirement_trends)

    content_pool_retirement_trends = create_content_retirement_trends(
        TYPE_POOL,
        retirement_trend_inputs
    )
    cache.set("content_pool_retirement_trends", content_pool_retirement_trends)

    content_chain_retirement_trends = create_content_retirement_trends(
        TYPE_CHAIN,
        retirement_trend_inputs
    )
    cache.set("content_chain_retirement_trends",
              content_chain_retirement_trends)

    content_beneficiary_retirement_trends = create_content_retirement_trends(
        TYPE_BENEFICIARY,
        retirement_trend_inputs
    )
    cache.set("content_beneficiary_retirement_trends",
              content_beneficiary_retirement_trends)

    # --- onchain carbon pool comparison ---
    fig_historical_prices = historical_prices(
        tokens_dict, df_prices, current_price_only_token_list
    )
    content_onchain_pool_comp = create_onchain_pool_comp_content(
        tokens_dict, df_prices, fig_historical_prices, price_source
    )
    cache.set("content_onchain_pool_comp", content_onchain_pool_comp)

    # --- homepage ---
    df_offchain, df_offchain_retired, df_onchain, df_onchain_retired = off_vs_on_data(
        df_verra, df_verra_retired, bridges_info_dict, retires_info_dict
    )

    fig_on_vs_off_time, fig_on_vs_off_time_download = create_offchain_vs_onchain_fig(
        df_offchain, df_offchain_retired, df_onchain, df_onchain_retired
    )

    df_retired_merged = merge_retirements_data_for_retirement_chart(
        df_retired, df_pool_retired, df_retired_mco2, df_retired_mco2_info
    )

    df_retirements, retirements_data, retirements_style_dict = create_retirements_data(
        df_retired_merged
    )
    df_holders, holders_data, holders_style_dict = create_holders_data(df_holdings)
    fig_retirements, fig_retirements_download = create_retirements_fig(
        retirements_data, retirements_style_dict
    )
    fig_holders, fig_holders_download = create_retirements_fig(
        holders_data, holders_style_dict
    )
    content_homepage = create_homepage_content(
        curr_time_str,
        df_retired,
        df_offchain,
        df_offchain_retired,
        df_onchain,
        df_onchain_retired,
        df_retirements,
        df_holders,
        fig_on_vs_off_time,
        fig_retirements,
        fig_holders,
    )
    cache.set("content_homepage", content_homepage)
    cache.set("fig_retirements", fig_retirements_download)
    cache.set("fig_holders", fig_holders_download)
    cache.set("fig_on_vs_off_time", fig_on_vs_off_time_download)

    sidebar_toggle = dbc.Row(
        [
            dbc.Col(
                html.Button(
                    html.Span("menu", className="material-icons"),
                    className="navbar-toggler",
                    id="toggle",
                ),
                width="auto",
                align="center",
            ),
        ]
    )

    sidebar_header = [
        html.A(
            [html.Img(src="assets/KlimaDAO-Wordmark-2.png", className="klima-logo")],
            href="https://www.klimadao.finance/",
            target="_blank",
            style={"padding-bottom": "24px"},
        ),
        # html.Hr(),
        # html.H3(
        #     "Tokenized Carbon Dashboards Beta",
        #     style={"textAlign": "start"},
        #     className="dashboard-title",
        # ),
        # html.Hr(style={"margin-bottom": "1.5rem"}),
    ]

    sidebar = html.Div(
        [
            dbc.Nav(
                sidebar_header
                + [
                    # html.H4("Top Level Summary", style={"textAlign": "left"}),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Span("token", className="material-icons"),
                                className="icon-container",
                            ),
                            html.Span("Digital Carbon Overview"),
                        ],
                        href="/",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Span("link", className="material-icons"),
                                className="icon-container",
                            ),
                            html.Span(
                                "Off vs On-Chain Carbon",
                            ),
                        ],
                        href="/carbon-market",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Span("balance", className="material-icons"),
                                className="icon-container",
                            ),
                            html.Span("Digital Carbon Pricing"),
                        ],
                        href="/carbon-pricing",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/carbon-supply-icon.svg",
                                    className="image-icons",
                                ),
                                className="icon-container",
                            ),
                            html.Span("Digital Carbon Supply"),
                        ],
                        href="/carbon-supply",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/retirement-trends-icon.svg",
                                    className="image-icons",
                                ),
                                className="icon-container",
                            ),
                            html.Span("Retirement Trends"),
                        ],
                        href="/retirements",
                        active="partial",
                    ),
                    # html.Hr(style={"margin-top": "1.5rem"}),
                    html.A(
                        html.P("C3", className="sidebar-protocol-heading"),
                        href="https://www.c3.app/",
                        target="_blank",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/C3_Logo_Cloud.png",
                                    className="moss-logo",
                                ),
                                className="icon-container",
                            ),
                            html.Span("C3T Overview"),
                        ],
                        href="/c3t",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/C3-UBO-Logo.png",
                                    className="image-icons",
                                ),
                                className="icon-container",
                            ),
                            html.Span("UBO Pool"),
                        ],
                        href="/ubo",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/C3-NBO-Logo.png",
                                    className="image-icons",
                                ),
                                className="icon-container",
                            ),
                            html.Span("NBO Pool"),
                        ],
                        href="/nbo",
                        active="exact",
                    ),
                    # html.Hr(style={"margin-top": "1.5rem"}),
                    html.A(
                        html.P("Moss", className="sidebar-protocol-heading"),
                        href="https://mco2token.moss.earth/",
                        target="_blank",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/MCO2-Logo.png", className="moss-logo"
                                ),
                                className="icon-container",
                            ),
                            html.Span("MCO2 Overview"),
                        ],
                        href="/mco2",
                        active="exact",
                    ),
                    # html.Hr(style={"margin-top": "1.5rem"}),
                    html.A(
                        html.P("Toucan", className="sidebar-protocol-heading"),
                        href="https://toucan.earth/",
                        target="_blank",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/TCO2-Logo.png", className="image-icons"
                                ),
                                className="icon-container",
                            ),
                            html.Span("TCO2 Overview"),
                        ],
                        href="/tco2",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/BCT-Logo.png", className="moss-logo"
                                ),
                                className="icon-container",
                            ),
                            html.Span("BCT Pool"),
                        ],
                        href="/bct",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Div(
                                html.Img(
                                    src="assets/NCT-Logo.png", className="moss-logo"
                                ),
                                className="icon-container",
                            ),
                            html.Span("NCT Pool"),
                        ],
                        href="/nct",
                        active="exact",
                        style={"margin-bottom": "30px"},
                    ),
                    # html.Hr(style={"margin-top": "3rem"}),
                ],
                vertical=True,
                pills=True,
                style={"gap": "4px"},
            )
        ],
        className="sidebar",
    )

    sidebar_mobile = html.Div(
        [
            dbc.Offcanvas(
                [
                    dbc.Nav(
                        sidebar_header
                        + [
                            # html.H4("Top Level Summary", style={"textAlign": "left"}),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Span("token", className="material-icons"),
                                        className="icon-container",
                                    ),
                                    html.Span(
                                        "Digital Carbon Overview",
                                    ),
                                ],
                                href="/",
                                active="exact",
                                id="button-homepage",
                                n_clicks=0,
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Span("link", className="material-icons"),
                                        className="icon-container",
                                    ),
                                    html.Span(
                                        "Off vs On-Chain Carbon",
                                    ),
                                ],
                                href="/carbon-market",
                                active="exact",
                                id="button-off_vs_on_chain",
                                n_clicks=0,
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Span(
                                            "balance", className="material-icons"
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span("Digital Carbon Pricing"),
                                ],
                                href="/carbon-pricing",
                                active="exact",
                                id="button-onchain_pool_comp",
                                n_clicks=0,
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/carbon-supply-icon.svg",
                                            className="image-icons",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span(
                                        "Digital Carbon Supply",
                                    ),
                                ],
                                href="/carbon-supply",
                                active="exact",
                                id="button-onchain_carbon_supply",
                                n_clicks=0,
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/retirement-trends-icon.svg",
                                            className="image-icons",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span(
                                        "Retirement Trends",
                                    ),
                                ],
                                href="/retirements",
                                active="partial",
                                id="button-retirement_trends",
                                n_clicks=0,
                            ),
                            # html.Hr(style={"margin-top": "1.5rem"}),
                            html.A(
                                html.P("C3", className="sidebar-protocol-heading"),
                                href="https://www.c3.app/",
                                target="_blank",
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/C3_Logo_Cloud.png",
                                            className="moss-logo",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span("C3T Overview"),
                                ],
                                href="/c3t",
                                active="exact",
                                id="button-c3t",
                                n_clicks=0,
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/C3-UBO-Logo.png",
                                            className="image-icons",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span("UBO Pool"),
                                ],
                                href="/ubo",
                                active="exact",
                                id="button-ubo",
                                n_clicks=0,
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/C3-NBO-Logo.png",
                                            className="image-icons",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span("NBO Pool"),
                                ],
                                href="/nbo",
                                active="exact",
                                id="button-nbo",
                                n_clicks=0,
                            ),
                            # html.Hr(style={"margin-top": "1.5rem"}),
                            html.A(
                                html.P("Moss", className="sidebar-protocol-heading"),
                                href="https://mco2token.moss.earth/",
                                target="_blank",
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/MCO2-Logo.png",
                                            className="moss-logo",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span("MCO2 Overview"),
                                ],
                                href="/mco2",
                                active="exact",
                                id="button-mco2",
                                n_clicks=0,
                            ),
                            # html.Hr(style={"margin-top": "1.5rem"}),
                            html.A(
                                html.P("Toucan", className="sidebar-protocol-heading"),
                                href="https://toucan.earth/",
                                target="_blank",
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/TCO2-Logo.png",
                                            className="image-icons",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span("TCO2 Overview"),
                                ],
                                href="/tco2",
                                active="exact",
                                id="button-tco2",
                                n_clicks=0,
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/BCT-Logo.png",
                                            className="moss-logo",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span("BCT Pool"),
                                ],
                                href="/bct",
                                active="exact",
                                id="button-bct",
                                n_clicks=0,
                            ),
                            dbc.NavLink(
                                [
                                    html.Div(
                                        html.Img(
                                            src="assets/NCT-Logo.png",
                                            className="moss-logo",
                                        ),
                                        className="icon-container",
                                    ),
                                    html.Span("NCT Pool"),
                                ],
                                href="/nct",
                                active="exact",
                                id="button-nct",
                                n_clicks=0,
                            ),
                            # html.Hr(style={"margin-top": "3rem"}),
                        ],
                        vertical=True,
                        pills=True,
                        style={"gap": "4px"},
                    ),
                    dbc.Button(
                        [
                            "Open the app",
                            html.Div(
                                html.Span(
                                    "open_in_new",
                                    className="material-icons",
                                ),
                                className="klimadao-app-icon-container",
                            ),
                        ],
                        className="klimadao-app-btn-sidebar",
                        href="https://app.klimadao.finance/#/stake",
                        target="_blank",
                    ),
                ],
                id="collapse",
                className="collapse",
                is_open=False,
            ),
        ],
        className="sidebar_mobile",
    )

    content = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(sidebar_toggle, width=3, style={"padding": "0px"}),
                    dbc.Col(),
                    dbc.Col(
                        html.Div(
                            [
                                dbc.Button(
                                    [
                                        "Open the app",
                                        html.Div(
                                            html.Span(
                                                "open_in_new",
                                                className="material-icons",
                                            ),
                                            className="klimadao-app-icon-container",
                                        ),
                                    ],
                                    className="klimadao-app-btn",
                                    href="https://app.klimadao.finance/#/stake",
                                    target="_blank",
                                ),
                            ],
                            className="top-btns",
                        ),
                        lg=5,
                        md=7,
                        style={
                            "padding": "0px",
                            "display": "flex",
                            "justify-content": "right",
                        },
                    ),
                ],
                className="toggler-row",
            ),
            sidebar_mobile,
            html.Div(
                id="page-content",
                children=[],
                style={"padding-top": "5px"},
            ),
        ],
        id="static-content",
    )

    footer = html.Div(
        html.P(["last updated ", html.Span(curr_time_str)]), className="footer"
    )

    layout = html.Div([dcc.Location(id="url"), sidebar, content, footer])
    return layout


app.layout = generate_layout


@callback(
    Output(component_id="Last X Days", component_property="children"),
    Output(component_id="volume plot", component_property="figure"),
    Output(component_id="vintage plot", component_property="figure"),
    Output(component_id="map", component_property="figure"),
    Output(component_id="methodology", component_property="figure"),
    Output(component_id="projects", component_property="figure"),
    Input(component_id="summary_type", component_property="value"),
    Input(component_id="bridged_or_retired", component_property="value"),
)
def update_output_div_tc(summary_type, TCO2_type):
    if summary_type == "Last 7 Days Performance":
        if TCO2_type == "Bridged":
            fig_seven_day = cache.get("fig_seven_day_tc")
            return (
                "Last 7 Days Performance",
                fig_seven_day[0],
                fig_seven_day[1],
                fig_seven_day[2],
                fig_seven_day[3],
                fig_seven_day[4],
            )
        elif TCO2_type == "Retired":
            fig_seven_day_retired = cache.get("fig_seven_day_retired_tc")
            return (
                "Last 7 Days Performance",
                fig_seven_day_retired[0],
                fig_seven_day_retired[1],
                fig_seven_day_retired[2],
                fig_seven_day_retired[3],
                fig_seven_day_retired[4],
            )

    elif summary_type == "Last 30 Days Performance":
        if TCO2_type == "Bridged":
            fig_thirty_day = cache.get("fig_thirty_day_tc")
            return (
                "Last 30 Days Performance",
                fig_thirty_day[0],
                fig_thirty_day[1],
                fig_thirty_day[2],
                fig_thirty_day[3],
                fig_thirty_day[4],
            )
        elif TCO2_type == "Retired":
            fig_thirty_day_retired = cache.get("fig_thirty_day_retired_tc")
            return (
                "Last 30 Days Performance",
                fig_thirty_day_retired[0],
                fig_thirty_day_retired[1],
                fig_thirty_day_retired[2],
                fig_thirty_day_retired[3],
                fig_thirty_day_retired[4],
            )

    elif summary_type == "Lifetime Performance":
        if TCO2_type == "Bridged":
            fig_total = cache.get("fig_total_tc")
            return (
                "Lifetime Performance",
                fig_total[0],
                fig_total[1],
                fig_total[2],
                fig_total[3],
                fig_total[4],
            )
        elif TCO2_type == "Retired":
            fig_total_retired = cache.get("fig_total_retired_tc")
            return (
                "Lifetime Performance",
                fig_total_retired[0],
                fig_total_retired[1],
                fig_total_retired[2],
                fig_total_retired[3],
                fig_total_retired[4],
            )


@callback(
    Output(component_id="Last X Days_c3t", component_property="children"),
    Output(component_id="volume plot_c3t", component_property="figure"),
    Output(component_id="vintage plot_c3t", component_property="figure"),
    Output(component_id="map_c3t", component_property="figure"),
    Output(component_id="methodology_c3t", component_property="figure"),
    Output(component_id="projects_c3t", component_property="figure"),
    Input(component_id="summary_type_c3t", component_property="value"),
    Input(component_id="bridged_or_retired_c3t", component_property="value"),
)
def update_output_div_c3(summary_type, C3T_type):
    if summary_type == "Last 7 Days Performance":
        if C3T_type == "Bridged":
            fig_seven_day = cache.get("fig_seven_day_c3t")
            return (
                "Last 7 Days Performance",
                fig_seven_day[0],
                fig_seven_day[1],
                fig_seven_day[2],
                fig_seven_day[3],
                fig_seven_day[4],
            )
        elif C3T_type == "Retired":
            fig_seven_day_retired = cache.get("fig_seven_day_retired_c3t")
            return (
                "Last 7 Days Performance",
                fig_seven_day_retired[0],
                fig_seven_day_retired[1],
                fig_seven_day_retired[2],
                fig_seven_day_retired[3],
                fig_seven_day_retired[4],
            )

    elif summary_type == "Last 30 Days Performance":
        if C3T_type == "Bridged":
            fig_thirty_day = cache.get("fig_thirty_day_c3t")
            return (
                "Last 30 Days Performance",
                fig_thirty_day[0],
                fig_thirty_day[1],
                fig_thirty_day[2],
                fig_thirty_day[3],
                fig_thirty_day[4],
            )
        elif C3T_type == "Retired":
            fig_thirty_day_retired = cache.get("fig_thirty_day_retired_c3t")
            return (
                "Last 30 Days Performance",
                fig_thirty_day_retired[0],
                fig_thirty_day_retired[1],
                fig_thirty_day_retired[2],
                fig_thirty_day_retired[3],
                fig_thirty_day_retired[4],
            )

    elif summary_type == "Lifetime Performance":
        if C3T_type == "Bridged":
            fig_total = cache.get("fig_total_c3t")
            return (
                "Lifetime Performance",
                fig_total[0],
                fig_total[1],
                fig_total[2],
                fig_total[3],
                fig_total[4],
            )
        elif C3T_type == "Retired":
            fig_total_retired = cache.get("fig_total_retired_c3t")
            return (
                "Lifetime Performance",
                fig_total_retired[0],
                fig_total_retired[1],
                fig_total_retired[2],
                fig_total_retired[3],
                fig_total_retired[4],
            )


@callback(
    Output(component_id="offchain-volume-title", component_property="children"),
    Output(component_id="onchain-volume-title", component_property="children"),
    Output(component_id="on_vs_off_vintage_title", component_property="children"),
    Output(component_id="on_vs_off_origin_title", component_property="children"),
    Output(component_id="on_vs_off_project_title", component_property="children"),
    Output(component_id="offchain-volume-plot", component_property="figure"),
    Output(component_id="onchain-volume-plot", component_property="figure"),
    Output(component_id="on_vs_off_vintage_plot", component_property="figure"),
    Output(component_id="on_vs_off_origin_plot", component_property="figure"),
    Output(component_id="on_vs_off_project_plot", component_property="figure"),
    Output(component_id="on_vs_off_vintage_footer", component_property="children"),
    Output(component_id="on_vs_off_origin_footer", component_property="children"),
    Output(component_id="on_vs_off_project_footer", component_property="children"),
    Input(component_id="issued_or_retired", component_property="value"),
)
def update_output_on_vs_off(type):

    if type == "Issued":
        titles_on_vs_off_issued = cache.get("titles_on_vs_off_issued")
        fig_on_vs_off_issued = cache.get("fig_on_vs_off_issued")
        return (
            titles_on_vs_off_issued[0],
            titles_on_vs_off_issued[1],
            titles_on_vs_off_issued[2],
            titles_on_vs_off_issued[3],
            titles_on_vs_off_issued[4],
            fig_on_vs_off_issued[0],
            fig_on_vs_off_issued[1],
            fig_on_vs_off_issued[2],
            fig_on_vs_off_issued[3],
            fig_on_vs_off_issued[4],
            None,
            None,
            None,
        )
    elif type == "Retired":
        moss_note = "Note: Project metadata of Moss Retired VCUs is unavailable"
        titles_on_vs_off_retired = cache.get("titles_on_vs_off_retired")
        fig_on_vs_off_retired = cache.get("fig_on_vs_off_retired")
        return (
            titles_on_vs_off_retired[0],
            titles_on_vs_off_retired[1],
            titles_on_vs_off_retired[2],
            titles_on_vs_off_retired[3],
            titles_on_vs_off_retired[4],
            fig_on_vs_off_retired[0],
            fig_on_vs_off_retired[1],
            fig_on_vs_off_retired[2],
            fig_on_vs_off_retired[3],
            fig_on_vs_off_retired[4],
            moss_note,
            moss_note,
            moss_note,
        )


@callback(
    Output(component_id="eligible pie chart plot", component_property="figure"),
    Input(component_id="pie_chart_summary", component_property="value"),
)
def update_eligible_pie_chart(pool_key):
    df_carbon = cache.get("df_carbon")
    fig_eligible_pool_pie_chart = eligible_pool_pie_chart(df_carbon, pool_key)
    return fig_eligible_pool_pie_chart


@app.callback(
    Output("download_image_retirements", "data"),
    Input("download_btn_retirements", "n_clicks"),
    prevent_initial_call=True,
)
def download_retirements(n_clicks):
    fig = cache.get("fig_retirements")
    filename = "Retirements.html"
    return dict(content=fig.to_html(), filename=filename)


@app.callback(
    Output("download_image_holders", "data"),
    Input("download_btn_holders", "n_clicks"),
    prevent_initial_call=True,
)
def download_holders(n_clicks):
    fig = cache.get("fig_holders")
    filename = "Holders.html"
    return dict(content=fig.to_html(), filename=filename)


@app.callback(
    Output("download_image_carbonmarket", "data"),
    Input("download_btn_carbonmarket", "n_clicks"),
    prevent_initial_call=True,
)
def download_carbonmarket(n_clicks):
    fig = cache.get("fig_on_vs_off_time")
    filename = "CarbonMarket.html"
    return dict(content=fig.to_html(), filename=filename)


@app.callback(
    Output("download_csv_BCT", "data"),
    Input("download_btn_BCT", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv_BCT_callback(n_clicks):
    df = cache.get("bct_carbon")
    filename = "BCT.csv"
    return dcc.send_data_frame(df.to_csv, filename=filename, index=False)


@app.callback(
    Output("download_csv_NCT", "data"),
    Input("download_btn_NCT", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv_NCT_callback(n_clicks):
    df = cache.get("nct_carbon")
    filename = "NCT.csv"
    return dcc.send_data_frame(df.to_csv, filename=filename, index=False)


@app.callback(
    Output("download_csv_UBO", "data"),
    Input("download_btn_UBO", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv_UBO_callback(n_clicks):
    df = cache.get("ubo_carbon")
    filename = "UBO.csv"
    return dcc.send_data_frame(df.to_csv, filename=filename, index=False)


@app.callback(
    Output("download_csv_NBO", "data"),
    Input("download_btn_NBO", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv_NBO_callback(n_clicks):
    df = cache.get("nbo_carbon")
    filename = "NBO.csv"
    return dcc.send_data_frame(df.to_csv, filename=filename, index=False)


@app.callback(
    Output("download_csv_MCO2", "data"),
    Input("download_btn_MCO2", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv_MCO2_callback(n_clicks):
    df = cache.get("mco2_carbon")
    filename = "MCO2.csv"
    return dcc.send_data_frame(df.to_csv, filename=filename, index=False)


app.clientside_callback(
    """
function copyToClipboard(n_clicks) {
    navigator.clipboard.writeText("https://carbon.klimadao.finance/");
}
""",
    Output("copy_website_clipboard_hidden_carbonmarket", "children"),
    Input("copy_website_clipboard_carbonmarket", "n_clicks"),
)

app.clientside_callback(
    """
function copyToClipboard(n_clicks) {
    navigator.clipboard.writeText("https://carbon.klimadao.finance/");
}
""",
    Output("copy_website_clipboard_hidden_holders", "children"),
    Input("copy_website_clipboard_holders", "n_clicks"),
)

app.clientside_callback(
    """
function copyToClipboard(n_clicks) {
    navigator.clipboard.writeText("https://carbon.klimadao.finance/");
}
""",
    Output("copy_website_clipboard_hidden_retirements", "children"),
    Input("copy_website_clipboard_retirements", "n_clicks"),
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    # For case-insensitive routing
    # NOTE: all `/` paths MUST be lowercase!
    pathname = pathname.lower()
    if pathname == "/":
        content_homepage = cache.get("content_homepage")
        return content_homepage
    elif pathname == "/carbon-market":
        content_offchain_vs_onchain = cache.get("content_offchain_vs_onchain")
        return content_offchain_vs_onchain

    elif pathname == "/carbon-pricing":
        content_onchain_pool_comp = cache.get("content_onchain_pool_comp")
        return content_onchain_pool_comp

    elif pathname == "/carbon-supply":
        content_carbon_supply = cache.get("content_carbon_supply")
        return content_carbon_supply

    elif pathname == "/retirements":
        content_carbon_supply = cache.get("content_pool_retirement_trends")
        return content_carbon_supply

    elif pathname == "/retirements/token":
        content_carbon_supply = cache.get("content_token_retirement_trends")
        return content_carbon_supply

    elif pathname == "/retirements/chain":
        content_carbon_supply = cache.get("content_chain_retirement_trends")
        return content_carbon_supply

    elif pathname == "/retirements/beneficiary":
        content_carbon_supply = cache.get("content_beneficiary_retirement_trends")
        return content_carbon_supply

    elif pathname == "/tco2":
        content_tco2 = cache.get("content_tco2")
        return content_tco2

    elif pathname == "/bct":
        content_bct = cache.get("content_bct")
        return content_bct

    elif pathname == "/nct":
        content_nct = cache.get("content_nct")
        return content_nct

    elif pathname == "/mco2":
        content_mco2 = cache.get("content_mco2")
        return content_mco2

    elif pathname == "/c3t":
        content_c3t = cache.get("content_c3t")
        return content_c3t

    elif pathname == "/ubo":
        content_ubo = cache.get("content_ubo")
        return content_ubo

    elif pathname == "/nbo":
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
    [
        Input("toggle", "n_clicks"),
        Input("button-homepage", "n_clicks"),
        Input("button-off_vs_on_chain", "n_clicks"),
        Input("button-onchain_pool_comp", "n_clicks"),
        Input("button-onchain_carbon_supply", "n_clicks"),
        Input("button-tco2", "n_clicks"),
        Input("button-bct", "n_clicks"),
        Input("button-nct", "n_clicks"),
        Input("button-mco2", "n_clicks"),
        Input("button-c3t", "n_clicks"),
        Input("button-ubo", "n_clicks"),
        Input("button-nbo", "n_clicks"),
    ],
    [State("collapse", "is_open")],
)
def toggle_collapse(
    n,
    n_home,
    n_off_vs_on,
    n_all_carbon_pools,
    n_carbon_supply,
    n_tco2,
    n_bct,
    n_nct,
    n_mco2,
    n_c3t,
    n_ubo,
    n_nbo,
    is_open,
):
    if (
        n
        or n_home
        or n_off_vs_on
        or n_all_carbon_pools
        or n_carbon_supply
        or n_tco2
        or n_bct
        or n_nct
        or n_mco2
        or n_c3t
        or n_ubo
        or n_nbo
    ):
        return not is_open
    return is_open


# For Gunicorn to reference
server = app.server


# Redirects
redirects = {
    "carbonmarket": "carbon-market",
    "Carbonmarket": "carbon-market",
    "carbonpricing": "carbon-pricing",
    "CarbonPricing": "carbon-pricing",
    "carbonsupply": "carbon-supply",
    "CarbonSupply": "carbon-supply",
    "TCO2": "tco2",
    "BCT": "bct",
    "NCT": "nct",
    "MCO2": "mco2",
    "C3T": "c3t",
    "UBO": "ubo",
    "NBO": "nbo",
}

for o, d in redirects.items():
    dash.register_page(__name__, path=f"/{d}", redirect_from=[f"/{o}"])


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
