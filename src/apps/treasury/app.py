import dash_bootstrap_components as dbc
from dash import Dash

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="KlimaDAO Treasury Dashboard",
    use_pages=True,
    meta_tags=[
        {
            'name': 'viewport',
            'content':
            'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'
        },
        {"property": "og:type", "content": "website"},
        {"property": "og:site_name", "content": "KlimaDAO Treasury Dashboard"},
        {"property": "og:title", "content": "Overview of KlimaDAO treasury composition and Green Ratio status"},
        {
            "property": "og:description",
            "content":
            "Overview of the inner workings of "
            "KlimaDAO's carbon-backed reserve currency protocol."
        },
        {
            "property": "og:image",
            "content": "https://static.wixstatic.com/media/5f17af_bfd51fccab89436e82f2cc2911097544~mv2.png/v1/fill/w_1306,h_734,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/5f17af_bfd51fccab89436e82f2cc2911097544~mv2.png"  # noqa: E501
        },
        {"name": "twitter:card", "content": "summary_large_image"},
        {"name": "twitter:site", "content": "@discord"},
        {"name": "twitter:creator", "content": "@KlimaDAO"}
    ]
)
