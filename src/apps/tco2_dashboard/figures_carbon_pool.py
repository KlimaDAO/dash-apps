import plotly.express as px
from .constants import FIGURE_BG_COLOR, GRAPH_FONT
import plotly.graph_objects as go
from .services import Offsets


def deposited_over_time(bridge, pool, status):
    offsets = Offsets().filter(bridge, pool, status).sum_over_time("Quantity")
    fig = px.area(offsets, x="Date", y="Quantity")
    fig.update_layout(
        height=300,
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
        margin=dict(t=50, b=0, l=0, r=0),
    )
    return fig


def deposited_over_time_s(df):
    df = df.sort_values(by="Date", ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(
        height=300,
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
        margin=dict(t=50, b=0, l=0, r=0),
    )
    return fig


def redeemed_over_time(df):
    df = df.sort_values(by="Date", ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(
        height=300,
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
        margin=dict(t=50, b=0, l=0, r=0),
    )
    return fig


def retired_over_time(pool_address, pool_name, df_pool_retired):
    fig = go.Figure()
    filtered_df = df_pool_retired
    filtered_df[f"Quantity_{pool_name}"] = filtered_df["Quantity"]
    filtered_df.loc[filtered_df["Pool"] != pool_address, f"Quantity_{pool_name}"] = 0
    filtered_df = filtered_df.sort_values(by="Date", ascending=True)
    filtered_df[f"Quantity_{pool_name}"] = filtered_df[f"Quantity_{pool_name}"].cumsum()
    fig = px.area(filtered_df, x="Date", y=f"Quantity_{pool_name}")
    fig.update_layout(
        height=300,
        xaxis_title="Date",
        yaxis_title="Quantity",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        font=GRAPH_FONT,
        margin=dict(t=50, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
    )
    return fig
