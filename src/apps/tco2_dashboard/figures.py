import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry
from .helpers import add_px_figure, human_format
from plotly.subplots import make_subplots
from .constants import (
    FIGURE_BG_COLOR,
    GRAPH_FONT,
    TREEMAP_FONT,
    PIE_CHART_FONT,
    GRAY,
    DARK_GRAY,
    WHITE
)
import pandas as pd
import circlify
import matplotlib
from base64 import b64encode
import math
from dash import dash_table
import datetime as dt
from .services import Offsets

matplotlib.use("agg")


def sub_plots_volume(bridge,
                       status,
                       date_range_days=None,
                       ):

    # Texts
    if status == "bridged":
        zero_status_text = "bridging"
        title_status_text = "Bridged"
    elif status == "retired":
        zero_status_text = "retiring"
        title_status_text = "Retired"
    else:
        raise Exception("Unknown offset status filter")

    zero_evt_text = (
        f"There haven't been any {zero_status_text} events<br>in the last {date_range_days} days"
    )
    title_indicator = f"Credits {title_status_text} ({date_range_days}d)"

    current_time = dt.datetime.combine(dt.date.today(), dt.datetime.min.time())
    period_start = current_time - dt.timedelta(days=date_range_days)
    last_period_start = period_start - dt.timedelta(days=date_range_days)

    # Base filter
    base_offsets = Offsets().filter(bridge, status)
    
    # Current data
    offsets = base_offsets.copy().date_range(period_start, current_time)
    df = offsets.get()
    quantity = offsets.copy().sum("Quantity")
    daily_quantity = offsets.copy().daily_agg().sum("Quantity")

    # Preceding data
    last_offsets = base_offsets.copy().date_range(last_period_start, period_start)
    last_df = last_offsets.get()
    last_quantity = last_offsets.copy().sum("Quantity")

    if not df.empty and quantity != 0:
        fig = make_subplots(
            rows=2,
            cols=1,
            specs=[[{"type": "domain"}], [{"type": "xy"}]],
            subplot_titles=("", ""),
            vertical_spacing=0.1,
        )
        fig.update_layout(font_color="white", margin=dict(t=20, b=0, l=0, r=0))

        if not last_df.empty and last_quantity != 0:
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=quantity,
                    title=dict(text=title_indicator, font=dict(size=12)),
                    number=dict(suffix="", font=dict(size=24)),
                    delta={
                        "position": "bottom",
                        "reference": last_quantity,
                        "relative": True,
                        "valueformat": ".1%",
                    },
                    domain={"x": [0.25, 0.75], "y": [0.6, 1]},
                )
            )
        else:
            fig.add_trace(
                go.Indicator(
                    mode="number",
                    value=quantity,
                    title=dict(text=title_indicator, font=dict(size=12)),
                    number=dict(suffix="", font=dict(size=24)),
                    domain={"x": [0.25, 0.75], "y": [0.6, 1]},
                )
            )

        add_px_figure(
            px.bar(
                daily_quantity.reset_index(),
                x="Date",
                y="Quantity",
                title="",
            ).update_traces(marker_line_width=0),
            fig,
            row=2,
            col=1,
        )

        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(title_text="Date", showgrid=False),
            yaxis=dict(title_text="Volume", showgrid=False),
            font=GRAPH_FONT,
            hovermode="x unified",
            hoverlabel=dict(font_color="white", font_size=8),
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(text=zero_evt_text, font=dict(color="white"), showarrow=False)
            ],
        )
    return fig


def sub_plots_vintage(df, last_df, title_indicator, title_graph, zero_evt_text):
    df = df[df["Vintage"] != "missing"].reset_index(drop=True)
    last_df = last_df[last_df["Vintage"] != "missing"].reset_index(drop=True)
    if not (df.empty):
        fig = make_subplots(
            rows=2,
            cols=1,
            specs=[[{"type": "domain"}], [{"type": "xy"}]],
            subplot_titles=("", title_graph),
            vertical_spacing=0.1,
        )
        fig.update_layout(font_color="white", margin=dict(t=20, b=0, l=0, r=0))
        if not (last_df.empty):
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=np.average(df["Vintage"], weights=df["Quantity"]),
                    number=dict(valueformat=".1f", font=dict(size=24)),
                    delta={
                        "reference": np.average(
                            last_df["Vintage"], weights=last_df["Quantity"]
                        ),
                        "valueformat": ".1f",
                    },
                    title=dict(text=title_indicator, font=dict(size=12)),
                    domain={"x": [0.25, 0.75], "y": [0.6, 1]},
                )
            )
        else:
            fig.add_trace(
                go.Indicator(
                    mode="number",
                    value=np.average(df["Vintage"], weights=df["Quantity"]),
                    number=dict(valueformat=".1f", font=dict(size=24)),
                    title=dict(text=title_indicator, font=dict(size=12)),
                    domain={"x": [0.25, 0.75], "y": [0.6, 1]},
                )
            )

        add_px_figure(
            px.bar(
                df.groupby("Vintage")["Quantity"].sum().to_frame().reset_index(),
                x="Vintage",
                y="Quantity",
                title=title_graph,
            ).update_traces(marker_line_width=0),
            fig,
            row=2,
            col=1,
        )
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(title_text="Vintage", showgrid=False),
            yaxis=dict(title_text="Volume", showgrid=False),
            font=GRAPH_FONT,
            hovermode="x unified",
            hoverlabel=dict(font_color="white", font_size=8),
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(text=zero_evt_text, font=dict(color="white"), showarrow=False)
            ],
        )
    return fig


country_cache: dict = dict()


def get_country(country):
    if country not in country_cache:
        res = None
        if country != "nan":
            res = pycountry.countries.search_fuzzy(country)[0].alpha_3
        country_cache[country] = res if res else country
    return country_cache[country]


def map(df, zero_evt_text):
    if not (df.empty):
        df = df[df["Country"] != "missing"].reset_index(drop=True)
        country_volumes = (
            df.groupby("Country")["Quantity"]
            .sum()
            .sort_values(ascending=False)
            .to_frame()
            .reset_index()
        )
        country_volumes["Country Code"] = [
            get_country(country) for country in country_volumes["Country"]
        ]
        country_volumes["text"] = country_volumes["Country Code"].astype(str)
        fig = px.choropleth(
            country_volumes,
            locations="Country Code",
            color="Quantity",
            hover_name="Country",
            # hover_data=['text'],
            # custom_data=['text'],
            color_continuous_scale=px.colors.sequential.Plasma,
            height=360,
        )

        fig.update_layout(
            height=360,
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                lakecolor="#4E5D6C",
                landcolor="darkgrey",
                subunitcolor="grey",
            ),
            font_color="white",
            dragmode=False,
            paper_bgcolor=FIGURE_BG_COLOR,
            hovermode="x unified",
            hoverlabel=dict(font_color="white", font_size=8),
            font=GRAPH_FONT,
            margin=dict(t=50, b=0, l=0, r=0),
            coloraxis_colorbar=dict(thickness=10, len=0.6),
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(text=zero_evt_text, font=dict(color="white"), showarrow=False)
            ],
        )
    return fig


def total_volume(df, title, zero_evt_text):
    if not (df.empty) and (df["Quantity"].sum() != 0):

        fig = make_subplots(
            rows=2,
            cols=1,
            specs=[[{"type": "domain"}], [{"type": "xy"}]],
            vertical_spacing=0.1,
            subplot_titles=("", ""),
        )
        fig.update_layout(font_color="white", margin=dict(t=20, b=0, l=0, r=0))

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=sum(df["Quantity"]),
                title=dict(text=title, font=dict(size=12)),
                number=dict(suffix="", font=dict(size=24)),
                domain={"x": [0.25, 0.75], "y": [0.6, 1]},
            )
        )

        add_px_figure(
            px.bar(
                df.groupby("Date")["Quantity"].sum().reset_index(),
                x="Date",
                y="Quantity",
                title="",
            ).update_traces(marker_line_width=0),
            fig,
            row=2,
            col=1,
        )

        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(title_text="Date", showgrid=False),
            yaxis=dict(title_text="Volume", showgrid=False),
            hovermode="x unified",
            hoverlabel=dict(font_color="white", font_size=8),
            font=GRAPH_FONT,
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(text=zero_evt_text, font=dict(color="white"), showarrow=False)
            ],
        )
    return fig


def total_vintage(df, zero_evt_text):
    df = df[df["Vintage"] != "missing"].reset_index(drop=True)
    if not (df.empty):
        value = np.average(df["Vintage"], weights=df["Quantity"])
        fig = make_subplots(
            rows=2,
            cols=1,
            specs=[[{"type": "domain"}], [{"type": "xy"}]],
            vertical_spacing=0.1,
            subplot_titles=("", ""),
        )
        fig.update_layout(font_color="white", margin=dict(t=20, b=0, l=0, r=0))

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=value,
                number=dict(valueformat=".1f", font=dict(size=24)),
                title=dict(text="Average Credit Vintage (total)", font=dict(size=12)),
                domain={"x": [0.25, 0.75], "y": [0.6, 1]},
            )
        )
        add_px_figure(
            px.bar(
                df.groupby("Vintage")["Quantity"].sum().to_frame().reset_index(),
                x="Vintage",
                y="Quantity",
                title="",
            ).update_traces(marker_line_width=0),
            fig,
            row=2,
            col=1,
        )

        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(title_text="Vintage", showgrid=False),
            yaxis=dict(title_text="Volume", showgrid=False),
            hovermode="x unified",
            hoverlabel=dict(font_color="white", font_size=8),
            font=GRAPH_FONT,
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(text=zero_evt_text, font=dict(color="white"), showarrow=False)
            ],
        )
    return fig


def methodology_volume(df, zero_evt_text):
    df = df[df["Methodology"] != "missing"].reset_index(drop=True)
    if not (df.empty):
        fig = px.bar(
            df.groupby("Methodology")["Quantity"].sum().to_frame().reset_index(),
            x="Methodology",
            y="Quantity",
            title="",
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            height=360,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            font_color="white",
            hovermode="x unified",
            hoverlabel=dict(font_color="white", font_size=8),
            font=GRAPH_FONT,
            margin=dict(t=50, b=0, l=0, r=0),
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(text=zero_evt_text, font=dict(color="white"), showarrow=False)
            ],
        )
    return fig


def project_volume(df, zero_evt_text):
    df = df[df["Project Type"] != "missing"].reset_index(drop=True)
    if not (df.empty):
        fig = px.treemap(
            df,
            path=[px.Constant("All Projects"), "Project Type", "Country", "Name"],
            values="Quantity",
            hover_data=["Name", "Quantity"],
            color_discrete_sequence=px.colors.qualitative.Antique,
            height=480,
            title="",
        )
        fig.update_traces(
            textfont=dict(color="white"),
            textinfo="label+value+percent parent+percent entry+percent root",
            texttemplate="<br>".join(
                [
                    "%{label}",
                    "Quantity=%{value}",
                    "%{percentParent} of Parent",
                    "%{percentEntry} of Entry",
                    "%{percentRoot} of Root",
                ]
            ),
        )
        fig.update_layout(
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            hoverlabel=dict(font_color="white", font_size=8),
            font=TREEMAP_FONT,
            margin=dict(t=50, b=20, l=0, r=0),
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(text=zero_evt_text, font=dict(color="white"), showarrow=False)
            ],
        )
    return fig


def project_volume_mco2(df, zero_evt_text):
    df = df[df["Project Type"] != "missing"].reset_index(drop=True)
    if not (df.empty):
        fig = px.treemap(
            df,
            path=[px.Constant("All Projects"), "Project Type", "Name"],
            values="Quantity",
            hover_data=["Name", "Quantity"],
            color_discrete_sequence=px.colors.qualitative.Antique,
            height=480,
            title="",
        )
        fig.update_traces(
            textfont=dict(color="white"),
            textinfo="label+value+percent parent+percent entry+percent root",
            texttemplate="<br>".join(
                [
                    "%{label}",
                    "Quantity=%{value}",
                    "%{percentParent} of Parent",
                    "%{percentEntry} of Entry",
                    "%{percentRoot} of Root",
                ]
            ),
        )
        fig.update_layout(
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            hoverlabel=dict(font_color="white", font_size=8),
            font=TREEMAP_FONT,
            margin=dict(t=20, b=20, l=0, r=0),
        )
    else:
        fig = go.Figure()
        fig.update_layout(
            height=300,
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(text=zero_evt_text, font=dict(color="white"), showarrow=False)
            ],
        )
    return fig


def pool_pie_chart(df, labels):
    values = [df[f"{i} Quantity"].sum() for i in labels]
    not_pool_qty = df["Total Quantity"].sum() - sum(values)
    values = values + [not_pool_qty]
    labels = labels + ["Not Pooled"]
    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            textinfo="percent",
            textfont=dict(color="white", size=12),
            hoverlabel=dict(font_color="white", font_size=8),
            hole=0.3,
        )
    )
    fig.update_layout(
        height=360,
        paper_bgcolor=FIGURE_BG_COLOR,
        font_color="white",
        font=PIE_CHART_FONT,
        margin=dict(t=50, b=0, l=0, r=0),
        legend=dict(x=1, font=dict(size=10)),
    )
    fig.update_traces(textposition="inside")

    return fig


def bridges_pie_chart(bridges_info_dict):
    labels = list(bridges_info_dict.keys())
    values = [d["Dataframe"]["Quantity"].sum() for d in bridges_info_dict.values()]
    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            textinfo="percent",
            textfont=dict(color="white", size=12),
            hoverlabel=dict(font_color="white", font_size=12),
            hole=0.3,
        )
    )
    fig.update_layout(
        height=360,
        paper_bgcolor=FIGURE_BG_COLOR,
        font_color="white",
        font=PIE_CHART_FONT,
        margin=dict(t=50, b=0, l=0, r=0),
        legend=dict(x=1, font=dict(size=12)),
    )
    fig.update_traces(textposition="inside")

    return fig


def eligible_pool_pie_chart(df, pool_key):
    if pool_key == "BCT":
        df = df[df["Vintage"] >= 2008].reset_index()
    elif pool_key == "NCT":
        df = df[df["Vintage"] >= 2012].reset_index()
    labels = [pool_key, f"NON_{pool_key}"]
    BCT = df[f"{pool_key} Quantity"].sum()
    Non_BCT = df["Total Quantity"].sum() - BCT
    values = [BCT, Non_BCT]
    fig_eligible = go.Figure()
    fig_eligible.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            textinfo="percent",
            textfont=dict(color="white", size=12),
            hoverlabel=dict(font_color="white", font_size=8),
            hole=0.3,
        )
    )
    fig_eligible.update_traces(marker=dict(colors=["red", "green"]))

    fig_eligible.update_layout(
        height=300,
        paper_bgcolor=FIGURE_BG_COLOR,
        font_color="white",
        font=PIE_CHART_FONT,
        margin=dict(t=0, b=0, l=0, r=0),
    )
    return fig_eligible


def verra_vintage(df_verra, df_verra_toucan):
    df_verra_toucan_grouped = (
        df_verra_toucan.groupby("Vintage")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_grouped = (
        df_verra.groupby("Vintage")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_other_grouped = df_verra_grouped.merge(
        df_verra_toucan_grouped,
        how="left",
        left_on="Vintage",
        right_on="Vintage",
        suffixes=("", "_Toucan"),
    )
    df_verra_other_grouped["Quantity_Toucan"] = df_verra_other_grouped[
        "Quantity_Toucan"
    ].fillna(0)
    df_verra_other_grouped["Quantity"] = (
        df_verra_other_grouped["Quantity"] - df_verra_other_grouped["Quantity_Toucan"]
    )
    df_verra_other_grouped = df_verra_other_grouped[["Vintage", "Quantity"]]
    df_verra_other_grouped["Type"] = "Rest of Issued VCU"
    df_verra_toucan_grouped["Type"] = "Toucan Bridged Credit"
    df_other_and_toucan = pd.concat(
        [df_verra_toucan_grouped, df_verra_other_grouped]
    ).reset_index()
    fig = px.bar(
        df_other_and_toucan,
        x="Vintage",
        y="Quantity",
        color="Type",
        title="",
        height=360,
    )
    fig.update_layout(
        height=360,
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        font_color="white",
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
        legend=dict(
            title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )

    return fig


def verra_map(df_verra, df_verra_toucan):
    df_verra_toucan_grouped = (
        df_verra_toucan.groupby("Country")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_grouped = (
        df_verra.groupby("Country")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_grouped = df_verra_grouped.merge(
        df_verra_toucan_grouped,
        how="left",
        left_on="Country",
        right_on="Country",
        suffixes=("", "_Toucan"),
    )
    df_verra_grouped["Quantity_Toucan"] = df_verra_grouped["Quantity_Toucan"].fillna(0)
    df_verra_grouped["Ratio"] = (
        df_verra_grouped["Quantity_Toucan"] / df_verra_grouped["Quantity"]
    )
    df_verra_grouped = df_verra_grouped[df_verra_grouped["Ratio"] != 0]
    df_verra_grouped["text"] = (
        df_verra_grouped["Country"]
        + "<br>"
        + "<br>"
        + "Tokenized Credits = "
        + df_verra_grouped["Quantity_Toucan"].map("{:,.0f}".format).astype(str)
        + "<br>"
        + "Verra Issued Credits = "
        + df_verra_grouped["Quantity"].map("{:,.0f}".format).astype(str)
        + "<br>"
        + "Ratio = "
        + df_verra_grouped["Ratio"].map("{:.4f}".format).astype(str)
        + "<br>"
    )
    df_verra_grouped = df_verra_grouped[df_verra_grouped["Country"] != ""].reset_index(
        drop=True
    )

    df_verra_grouped["Country Code"] = [
        get_country(country) for country in df_verra_grouped["Country"]
    ]
    fig = px.choropleth(
        df_verra_grouped,
        locations="Country Code",
        color="Ratio",
        hover_name="Country",
        custom_data=["text"],
        color_continuous_scale=px.colors.diverging.Picnic,
        height=360,
    )

    fig.update_traces(hovertemplate="%{customdata}")

    fig.update_layout(
        height=360,
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="#4E5D6C",
            landcolor="darkgrey",
            subunitcolor="grey",
        ),
        font_color="white",
        dragmode=False,
        paper_bgcolor=FIGURE_BG_COLOR,
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
        margin=dict(t=50, b=0, l=0, r=0),
        coloraxis_colorbar=dict(thickness=10, len=0.6),
    )
    return fig


def verra_project(df_verra, df_verra_toucan):
    df_verra_toucan_grouped = (
        df_verra_toucan.groupby("Project Type")["Quantity"]
        .sum()
        .to_frame()
        .reset_index()
    )
    df_verra_grouped = (
        df_verra.groupby("Project Type")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_other_grouped = df_verra_grouped.merge(
        df_verra_toucan_grouped,
        how="left",
        left_on="Project Type",
        right_on="Project Type",
        suffixes=("", "_Toucan"),
    )
    df_verra_other_grouped["Quantity_Toucan"] = df_verra_other_grouped[
        "Quantity_Toucan"
    ].fillna(0)
    df_verra_other_grouped["Quantity"] = (
        df_verra_other_grouped["Quantity"] - df_verra_other_grouped["Quantity_Toucan"]
    )
    df_verra_other_grouped["Type"] = "Rest of Issued VCU"
    df_verra_toucan_grouped["Type"] = "Toucan Bridged Credit"
    df_other_and_toucan = pd.concat(
        [df_verra_toucan_grouped, df_verra_other_grouped]
    ).reset_index()
    fig = px.treemap(
        df_other_and_toucan,
        path=[px.Constant("All Projects"), "Project Type", "Type"],
        values="Quantity",
        hover_data=["Type", "Quantity"],
        color_discrete_sequence=px.colors.qualitative.Antique,
        height=480,
        title="",
    )
    fig.update_traces(
        textfont=dict(color="white"),
        textinfo="label+value+percent parent+percent entry+percent root",
        texttemplate="<br>".join(
            [
                "%{label}",
                "Quantity=%{value}",
                "%{percentParent} of Parent",
                "%{percentEntry} of Entry",
                "%{percentRoot} of Root",
            ]
        ),
    )
    fig.update_layout(
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        hoverlabel=dict(font_color="white", font_size=8),
        font=TREEMAP_FONT,
        margin=dict(t=20, b=20, l=0, r=0),
    )

    return fig


def historical_prices(tokens_dict, df_prices, excluded_tokens):
    fig = go.Figure()
    for i in tokens_dict.keys():
        if i not in excluded_tokens:
            col_name = f"{i}_Price"
            a = df_prices[col_name].isna()
            filtered_df = df_prices[~a]
            fig.add_trace(
                go.Scatter(
                    x=filtered_df["Date"], y=filtered_df[col_name], mode="lines", name=i
                )
            )
    fig.update_layout(
        height=360,
        xaxis_title="Date",
        yaxis_title="Price",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=50, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
    )
    return fig


def token_klima_retirement_chart(tco2_df, mco2_df, c3t_df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=tco2_df.dailyKlimaRetirements_datetime,
            y=tco2_df.dailyKlimaRetirements_amount,
            mode="lines", name="TCO2"
        )),
    fig.add_trace(
        go.Scatter(
            x=mco2_df.dailyKlimaRetirements_datetime,
            y=mco2_df.dailyKlimaRetirements_amount,
            mode="lines", name="MCO2"
        )),
    fig.add_trace(
        go.Scatter(
            x=c3t_df.dailyKlimaRetirements_datetime,
            y=c3t_df.dailyKlimaRetirements_amount,
            mode="lines", name="C3T"
        ))
    fig.update_layout(
        height=360,
        xaxis_title="Date",
        yaxis_title="Tonnes Retired",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=50, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
    )
    return fig


def pool_klima_retirement_chart(bct_df, nct_df, mco2_df, ubo_df, nbo_df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=bct_df.dailyKlimaRetirements_datetime,
            y=bct_df.dailyKlimaRetirements_amount,
            mode="lines", name="BCT"
        )),
    fig.add_trace(
        go.Scatter(
            x=nct_df.dailyKlimaRetirements_datetime,
            y=nct_df.dailyKlimaRetirements_amount,
            mode="lines", name="NCT"
        )),
    fig.add_trace(
        go.Scatter(
            x=mco2_df.dailyKlimaRetirements_datetime,
            y=mco2_df.dailyKlimaRetirements_amount,
            mode="lines", name="MCO2"
        )),
    fig.add_trace(
        go.Scatter(
            x=ubo_df.dailyKlimaRetirements_datetime,
            y=ubo_df.dailyKlimaRetirements_amount,
            mode="lines", name="UBO"
        )),
    fig.add_trace(
        go.Scatter(
            x=nbo_df.dailyKlimaRetirements_datetime,
            y=nbo_df.dailyKlimaRetirements_amount,
            mode="lines", name="NBO"
        ))
    fig.update_layout(
        height=360,
        xaxis_title="Date",
        yaxis_title="Tonnes Retired",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=50, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
    )
    return fig


def chain_klima_retirement_chart(onchain_df, offchain_df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=onchain_df.dailyKlimaRetirements_datetime,
            y=onchain_df.dailyKlimaRetirements_amount,
            mode="lines", name="On chain"
        )),

    if offchain_df is not None:
        fig.add_trace(
            go.Scatter(
                x=offchain_df.Date,
                y=offchain_df.Quantity,
                mode="lines", name="Off chain"
            ))
    fig.update_layout(
        height=360,
        xaxis_title="Date",
        yaxis_title="Tonnes Retired",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=50, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
    )
    return fig


def pool_retired_chart(token_cg_dict, df_pool_retired):
    fig = go.Figure()
    for i in token_cg_dict.keys():
        pool_address = token_cg_dict[i]["address"]
        filtered_df = df_pool_retired
        filtered_df[f"Quantity_{i}"] = filtered_df["Quantity"]
        filtered_df.loc[filtered_df["Pool"] !=
                        pool_address, f"Quantity_{i}"] = 0
        filtered_df = filtered_df.sort_values(by="Date", ascending=True)
        filtered_df[f"Quantity_{i}"] = filtered_df[f"Quantity_{i}"].cumsum()
        fig.add_trace(
            go.Scatter(
                x=filtered_df["Date"],
                y=filtered_df[f"Quantity_{i}"],
                mode="lines",
                name=i,
                stackgroup="one",
            )
        )
    fig.update_layout(
        height=300,
        font=dict(color="white"),
        xaxis_title="Date",
        yaxis_title="Quantity",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=20, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8, font=GRAPH_FONT),
    )
    return fig


def tokenized_volume(bridges_info_dict):
    fig = go.Figure()
    for i in bridges_info_dict.keys():
        df = bridges_info_dict[i]["Dataframe"]
        df = df.sort_values(by="Date", ascending=True)
        df["Quantity"] = df["Quantity"].cumsum()
        df["Type"] = f"{i} Bridged Credits"
        fig.add_trace(
            go.Scatter(
                x=df["Date"], y=df["Quantity"], mode="lines", name=i, stackgroup="one"
            )
        )
        fig.update_layout(
            height=300,
            xaxis_title="Date",
            yaxis_title="Quantity",
            paper_bgcolor=FIGURE_BG_COLOR,
            plot_bgcolor=FIGURE_BG_COLOR,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            margin=dict(t=20, b=20, l=0, r=0),
            hovermode="x unified",
            hoverlabel=dict(font_color="white", font_size=8),
            font=GRAPH_FONT,
        )
    return fig


def on_vs_off_vintage(df_verra, bridges_info_dict):
    df_verra = df_verra[df_verra["Vintage"] != "missing"]
    df_verra_grouped = (
        df_verra.groupby("Vintage")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_other_grouped = pd.DataFrame()
    dfs = []
    for i in bridges_info_dict.keys():
        df = bridges_info_dict[i]["Dataframe"]
        df = df[df["Vintage"] != "missing"]
        df = df.groupby("Vintage")["Quantity"].sum().to_frame().reset_index()
        df["Type"] = f"{i} Bridged VCUs"
        dfs.append(df)
        if df_verra_other_grouped.empty:
            df_verra_other_grouped = df_verra_grouped.merge(
                df,
                how="left",
                left_on="Vintage",
                right_on="Vintage",
                suffixes=("", f"_{i}"),
            )
        else:
            df_verra_other_grouped = df_verra_other_grouped.merge(
                df,
                how="left",
                left_on="Vintage",
                right_on="Vintage",
                suffixes=("", f"_{i}"),
            )
        df_verra_other_grouped[f"Quantity_{i}"] = df_verra_other_grouped[
            f"Quantity_{i}"
        ].fillna(0)
        df_verra_other_grouped["Quantity"] = (
            df_verra_other_grouped["Quantity"] - df_verra_other_grouped[f"Quantity_{i}"]
        )
        df_verra_other_grouped = df_verra_other_grouped[["Vintage", "Quantity"]]
        df_verra_other_grouped["Type"] = "Rest of Issued VCUs"

    df_other_and_bridges = pd.concat(dfs + [df_verra_other_grouped]).reset_index()
    fig = px.bar(
        df_other_and_bridges,
        x="Vintage",
        y="Quantity",
        color="Type",
        title="",
        height=300,
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        height=360,
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        font=GRAPH_FONT,
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        legend=dict(
            title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        margin=dict(t=80, b=20, l=0, r=0),
    )

    return fig


def on_vs_off_vintage_retired(df_verra_retired, retires_info_dict):
    df_verra_retired = df_verra_retired[df_verra_retired["Vintage"] != "missing"]
    df_verra_grouped = (
        df_verra_retired.groupby("Vintage")["Quantity"].sum().to_frame().reset_index()
    )
    dfs = []
    for i in retires_info_dict.keys():
        df = retires_info_dict[i]["Dataframe"]
        df = df[df["Vintage"] != "missing"]
        df = df.groupby("Vintage")["Quantity"].sum().to_frame().reset_index()
        df["Type"] = f"{i} Retired VCUs"
        dfs.append(df)
    df_verra_grouped["Type"] = "Off-Chain Retired VCUs"

    df_other_and_bridges = pd.concat(dfs + [df_verra_grouped]).reset_index()
    fig = px.bar(
        df_other_and_bridges,
        x="Vintage",
        y="Quantity",
        color="Type",
        title="",
        height=300,
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        height=360,
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        font=GRAPH_FONT,
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        legend=dict(
            title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        margin=dict(t=80, b=20, l=0, r=0),
    )

    return fig


def on_vs_off_map(df_verra, bridges_info_dict):
    df_verra = df_verra[df_verra["Country"] != "missing"]
    df_verra_grouped = (
        df_verra.groupby("Country")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_grouped["Text_Bridges"] = ""
    df_verra_grouped["Quantity_Bridges"] = 0
    for i in bridges_info_dict.keys():
        df = bridges_info_dict[i]["Dataframe"]
        df = df[df["Country"] != "missing"]
        df = df.groupby("Country")["Quantity"].sum().to_frame().reset_index()
        df["Type"] = f"{i} Bridged VCUs"
        df_verra_grouped = df_verra_grouped.merge(
            df,
            how="left",
            left_on="Country",
            right_on="Country",
            suffixes=("", f"_{i}"),
        )
        df_verra_grouped[f"Quantity_{i}"] = df_verra_grouped[f"Quantity_{i}"].fillna(0)
        df_verra_grouped["Quantity_Bridges"] = (
            df_verra_grouped["Quantity_Bridges"] + df_verra_grouped[f"Quantity_{i}"]
        )
        df_verra_grouped["Text_Bridges"] = (
            df_verra_grouped["Text_Bridges"]
            + f"{i} Bridged VCUs = "
            + df_verra_grouped[f"Quantity_{i}"].map("{:,.0f}".format).astype(str)
            + "<br>"
        )
    df_verra_grouped["Percentage"] = (
        (df_verra_grouped["Quantity_Bridges"] / df_verra_grouped["Quantity"]) * 100
    ).round(decimals=4)
    df_verra_grouped["text"] = (
        df_verra_grouped["Country"]
        + "<br>"
        + "<br>"
        + df_verra_grouped["Text_Bridges"]
        + "Total Tokenized VCUs = "
        + df_verra_grouped["Quantity_Bridges"].map("{:,.0f}".format).astype(str)
        + "<br>"
        + "Verra Issued Credits = "
        + df_verra_grouped["Quantity"].map("{:,.0f}".format).astype(str)
        + "<br>"
        + "Percentage = "
        + df_verra_grouped["Percentage"].astype(str)
        + "%"
        + "<br>"
    )
    df_verra_grouped = df_verra_grouped[df_verra_grouped["Country"] != ""].reset_index(
        drop=True
    )
    df_verra_grouped["Country Code"] = [
        get_country(country) for country in df_verra_grouped["Country"]
    ]

    cut_bins = [-np.inf, 0, 2, 5, 10, 100]
    bin_labels = ["0", "(0-2]", "(2-5]", "(5-10]", "(10-100]"]
    df_verra_grouped["Percentage Bins"] = pd.cut(
        df_verra_grouped["Percentage"], bins=cut_bins, labels=bin_labels
    )
    df_verra_grouped = df_verra_grouped.sort_values(by=["Percentage"])

    fig = px.choropleth(
        df_verra_grouped,
        locations="Country Code",
        color="Percentage Bins",
        hover_name="Country",
        custom_data=["text"],
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        height=300,
    )

    fig.update_traces(hovertemplate="%{customdata}")

    fig.update_layout(
        height=360,
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="#4E5D6C",
            landcolor="darkgrey",
            subunitcolor="grey",
        ),
        dragmode=False,
        paper_bgcolor=FIGURE_BG_COLOR,
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
        margin=dict(t=20, b=20, l=0, r=0),
        legend=dict(
            font=dict(size=8),
            tracegroupgap=0,
            title="     Percentage <br> Tokenized Credits",
            y=0.5,
        ),
    )
    return fig


def on_vs_off_map_retired(df_verra_retired, retires_info_dict):
    df_verra_retired = df_verra_retired[df_verra_retired["Country"] != "missing"]
    df_verra_grouped = (
        df_verra_retired.groupby("Country")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_grouped["Text_Retires"] = ""
    df_verra_grouped["Quantity_Retires"] = 0
    for i in retires_info_dict.keys():
        df = retires_info_dict[i]["Dataframe"]
        df = df[df["Country"] != "missing"]
        df = df.groupby("Country")["Quantity"].sum().to_frame().reset_index()
        df["Type"] = f"{i} Retired VCUs"
        df_verra_grouped = df_verra_grouped.merge(
            df,
            how="left",
            left_on="Country",
            right_on="Country",
            suffixes=("", f"_{i}"),
        )
        df_verra_grouped[f"Quantity_{i}"] = df_verra_grouped[f"Quantity_{i}"].fillna(0)
        df_verra_grouped["Quantity_Retires"] = (
            df_verra_grouped["Quantity_Retires"] + df_verra_grouped[f"Quantity_{i}"]
        )
        df_verra_grouped["Text_Retires"] = (
            df_verra_grouped["Text_Retires"]
            + f"{i} Retired VCUs = "
            + df_verra_grouped[f"Quantity_{i}"].map("{:,.0f}".format).astype(str)
            + "<br>"
        )
    df_verra_grouped["Percentage"] = (
        (
            df_verra_grouped["Quantity_Retires"]
            / (df_verra_grouped["Quantity_Retires"] + df_verra_grouped["Quantity"])
        )
        * 100
    ).round(decimals=4)
    df_verra_grouped["text"] = (
        df_verra_grouped["Country"]
        + "<br>"
        + "<br>"
        + df_verra_grouped["Text_Retires"]
        + "Total On-Chain Retired VCUs = "
        + df_verra_grouped["Quantity_Retires"].map("{:,.0f}".format).astype(str)
        + "<br>"
        + "Total Verra Retired Credits = "
        + df_verra_grouped["Quantity"].map("{:,.0f}".format).astype(str)
        + "<br>"
        + "Percentage = "
        + df_verra_grouped["Percentage"].astype(str)
        + "%"
        + "<br>"
    )
    df_verra_grouped = df_verra_grouped[df_verra_grouped["Country"] != ""].reset_index(
        drop=True
    )

    df_verra_grouped["Country Code"] = [
        get_country(country) for country in df_verra_grouped["Country"]
    ]

    cut_bins = [-np.inf, 0, 2, 5, 10, 100]
    bin_labels = ["0", "(0-2]", "(2-5]", "(5-10]", "(10-100]"]
    df_verra_grouped["Percentage Bins"] = pd.cut(
        df_verra_grouped["Percentage"], bins=cut_bins, labels=bin_labels
    )
    df_verra_grouped = df_verra_grouped.sort_values(by=["Percentage"])

    fig = px.choropleth(
        df_verra_grouped,
        locations="Country Code",
        color="Percentage Bins",
        hover_name="Country",
        custom_data=["text"],
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        height=300,
    )

    fig.update_traces(hovertemplate="%{customdata}")

    fig.update_layout(
        height=360,
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="#4E5D6C",
            landcolor="darkgrey",
            subunitcolor="grey",
        ),
        dragmode=False,
        paper_bgcolor=FIGURE_BG_COLOR,
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
        margin=dict(t=20, b=20, l=0, r=0),
        legend=dict(
            font=dict(size=8),
            tracegroupgap=0,
            title=" Percentage On-Chain <br>    Retired Credits",
            y=0.5,
        ),
    )
    return fig


def on_vs_off_project(df_verra, bridges_info_dict):
    df_verra = df_verra[df_verra["Project Type"] != "missing"]
    df_verra_grouped = (
        df_verra.groupby("Project Type")["Quantity"].sum().to_frame().reset_index()
    )
    df_verra_other_grouped = pd.DataFrame()
    dfs = []
    colors = {}
    for i in bridges_info_dict.keys():
        df = bridges_info_dict[i]["Dataframe"]
        df = df[df["Project Type"] != "missing"]
        df = df.groupby("Project Type")["Quantity"].sum().to_frame().reset_index()
        df["Type"] = f"{i} Bridged VCUs"
        colors[f"{i} Bridged VCUs"] = "#00CC33"
        dfs.append(df)
        if df_verra_other_grouped.empty:
            df_verra_other_grouped = df_verra_grouped.merge(
                df,
                how="left",
                left_on="Project Type",
                right_on="Project Type",
                suffixes=("", f"_{i}"),
            )
        else:
            df_verra_other_grouped = df_verra_other_grouped.merge(
                df,
                how="left",
                left_on="Project Type",
                right_on="Project Type",
                suffixes=("", f"_{i}"),
            )
        df_verra_other_grouped[f"Quantity_{i}"] = df_verra_other_grouped[
            f"Quantity_{i}"
        ].fillna(0)
        df_verra_other_grouped["Quantity"] = (
            df_verra_other_grouped["Quantity"] - df_verra_other_grouped[f"Quantity_{i}"]
        )
        df_verra_other_grouped = df_verra_other_grouped[["Project Type", "Quantity"]]
        df_verra_other_grouped["Type"] = "Rest of Issued VCUs"
    colors["Rest of Issued VCUs"] = "#536C9C"
    colors["(?)"] = "#6E6E6E"
    df_other_and_bridges = pd.concat(dfs + [df_verra_other_grouped]).reset_index()
    fig = px.treemap(
        df_other_and_bridges,
        path=[px.Constant("All Projects"), "Project Type", "Type"],
        values="Quantity",
        color_discrete_map=colors,
        #  color_discrete_sequence=px.colors.qualitative.Antique,
        color="Type",
        hover_data=["Type", "Quantity"],
        height=480,
        title="",
    )
    fig.update_traces(
        textfont=dict(color="white"),
        textinfo="label+value+percent parent+percent entry+percent root",
        texttemplate="<br>".join(
            [
                "%{label}",
                "Quantity=%{value}",
                "%{percentParent} of Parent",
                "%{percentEntry} of Entry",
                "%{percentRoot} of Root",
            ]
        ),
    )
    fig.update_layout(
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        hoverlabel=dict(font_color="white", font_size=8),
        font=TREEMAP_FONT,
        margin=dict(t=20, b=20, l=0, r=0),
    )

    return fig


def on_vs_off_project_retired(df_verra_retired, retires_info_dict):
    df_verra_retired = df_verra_retired[df_verra_retired["Project Type"] != "missing"]
    df_verra_grouped = (
        df_verra_retired.groupby("Project Type")["Quantity"]
        .sum()
        .to_frame()
        .reset_index()
    )
    colors = {}
    dfs = []
    for i in retires_info_dict.keys():
        df = retires_info_dict[i]["Dataframe"]
        df = df[df["Project Type"] != "missing"]
        df = df.groupby("Project Type")["Quantity"].sum().to_frame().reset_index()
        df["Type"] = f"{i} Retired VCUs"
        colors[f"{i} Retired VCUs"] = "#00CC33"
        dfs.append(df)
    df_verra_grouped["Type"] = "Off-Chain Retired VCUs"
    colors["Off-Chain Retired VCUs"] = "#536C9C"
    colors["(?)"] = "#6E6E6E"
    df_other_and_bridges = pd.concat(dfs + [df_verra_grouped]).reset_index()
    fig = px.treemap(
        df_other_and_bridges,
        path=[px.Constant("All Projects"), "Project Type", "Type"],
        values="Quantity",
        color_discrete_map=colors,
        #  color_discrete_sequence=px.colors.qualitative.Antique,
        color="Type",
        hover_data=["Type", "Quantity"],
        height=480,
        title="",
    )
    fig.update_traces(
        textfont=dict(color="white"),
        textinfo="label+value+percent parent+percent entry+percent root",
        texttemplate="<br>".join(
            [
                "%{label}",
                "Quantity=%{value}",
                "%{percentParent} of Parent",
                "%{percentEntry} of Entry",
                "%{percentRoot} of Root",
            ]
        ),
    )
    fig.update_layout(
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        hoverlabel=dict(font_color="white", font_size=8),
        font=TREEMAP_FONT,
        margin=dict(t=20, b=20, l=0, r=0),
    )

    return fig


def create_offchain_vs_onchain_fig(
    df_offchain, df_offchain_retired, df_onchain, df_onchain_retired
):

    issued = df_offchain["Quantity"].iat[-1] + df_onchain["Quantity"].iat[-1]
    tokenized = df_onchain["Quantity"].iat[-1]
    offchain_retired = df_offchain_retired["Quantity"].iat[-1]
    onchain_retired = df_onchain_retired["Quantity"].iat[-1]

    label_value = [
        human_format(issued),
        human_format(offchain_retired),
        human_format(tokenized),
        human_format(onchain_retired),
    ]
    label_value = ["<b>" + i + "</b>" for i in label_value]
    fig = go.Figure()

    # Set axes properties
    fig.update_xaxes(
        range=[-1, 1],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        # scaleanchor="y",
        # scaleratio=1,
        # constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
    )

    fig.update_yaxes(
        range=[-1, 1],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        scaleanchor="x",
        scaleratio=1,
        # constrain='domain'
    )

    x_lst = [0.45, 0.66, -0.17, -0.17]
    y_lst = [0, 0, 0, -0.12]
    r_lst = [0.9, 0.6, 0.2, 0.05]
    color_lst = ["#0BA1FF", "#0BA1FF", "#44ffa8", "#00CC33"]
    opacity_lst = [0.5, 1, 0.8, 1]
    font_x = [0.45, 0.66, -0.25, -0.17]
    font_y = [0.80, 0, 0.15, -0.12]
    label_text = [
        "Verra Registry Credits Issued",
        "Retired Off-Chain",
        "Tokenized",
        "Tokenized & Retired",
    ]

    # add parent circles
    for i in range(4):
        # x, y, r = circle
        x = x_lst[i]
        y = y_lst[i]
        r = r_lst[i]
        if i < 3:
            fig.add_shape(
                type="circle",
                xref="x",
                yref="y",
                # x0=x - r * 0.75,
                # y0=y - r * 1.1,
                # x1=x + r * 0.75,
                # y1=y + r * 1.1,
                x0=x - r,
                y0=y - r,
                x1=x + r,
                y1=y + r,
                fillcolor=color_lst[i],  # fill color if needed
                line_color=color_lst[i],
                opacity=opacity_lst[i],
                line_width=2,
            )
        if i == 3:
            fig.add_shape(
                type="circle",
                xref="x",
                yref="y",
                x0=x - r,
                y0=y - r,
                x1=x + r,
                y1=y + r,
                fillcolor=color_lst[i],  # fill color if needed
                # line_color=color_lst[i],
                opacity=opacity_lst[i],
                line_width=1,
                line_color="white",
            )
        if i in [2, 3]:
            fig.add_annotation(
                x=font_x[i],
                y=font_y[i],
                xref="x",
                yref="y",
                text=label_value[i],
                showarrow=True,
                font=dict(size=30, color="white"),
                align="center",
                arrowhead=1,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor="white",
                ax=-0.75,
                ay=font_y[i],
                axref="x",
                ayref="y",
                # bordercolor="#c7c7c7",
                # borderwidth=2,
                # borderpad=4,
                # bgcolor="#ff7f0e",
                # opacity=0.8,
            )
            fig.add_annotation(
                x=-0.75,
                y=font_y[i] - 0.1,
                xref="x",
                yref="y",
                text=label_text[i],
                showarrow=False,
                font=dict(size=15, color="white"),
                align="center",
            )
        else:
            fig.add_annotation(
                x=font_x[i],
                y=font_y[i],
                xref="x",
                yref="y",
                text=label_value[i],
                showarrow=False,
                font=dict(size=30, color="white", family="Inter, sans-serif"),
                align="center",
            )
            fig.add_annotation(
                x=font_x[i],
                y=font_y[i] - 0.1,
                xref="x",
                yref="y",
                text=label_text[i],
                showarrow=False,
                font=dict(size=15, color="white", family="Inter, sans-serif"),
                align="center",
            )

    fig.update_layout(
        width=600,
        height=600,
        font=dict(color="white", family="Inter, sans-serif"),
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        # xaxis=dict(showgrid=True, visible=True),
        # yaxis=dict(showgrid=True, visible=True),
        margin=dict(t=0, b=0, l=0, r=0),
        showlegend=True,
    )

    img_bytes = fig.to_image(format="png", scale=3)
    encoding = b64encode(img_bytes).decode()
    img_b64 = "data:image/png;base64," + encoding

    return img_b64, fig


def font_size_calculator(label, r):
    if label == "<b>" + "..." + "</b>":
        font_size = 4
    else:
        font_size = max(10, math.ceil(min(25, (r / 0.5) * 25)))
    return font_size


def create_retirements_fig(data, style_dict):
    circles = circlify.circlify(
        data, show_enclosure=False, target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    fig = go.Figure()
    # Set axes properties
    fig.update_xaxes(
        range=[-1, 1],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        # scaleanchor="y",
        # scaleratio=1,
        # constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
    )

    fig.update_yaxes(
        range=[-1, 1],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        scaleanchor="x",
        scaleratio=1,
        # constrain='domain'
    )
    # Print circles:
    i = 1
    xmin = math.inf
    xmax = -math.inf
    ymin = math.inf
    ymax = -math.inf
    range_buffer = 0.05
    for circle in circles:
        if circle.level != 2:
            continue
        x, y, r = circle
        label = circle.ex["id"]
        label_value = "{:,}".format(int(circle.ex["datum"])) + "t"
        r = r * style_dict[label]["scale_r"]
        xmin = max(-1, min(xmin, x - r - range_buffer))
        xmax = min(1, max(xmax, x + r + range_buffer))
        ymin = max(-1, min(ymin, y - r - range_buffer))
        ymax = min(1, max(ymax, y + r + range_buffer))
        label_text = "<b>" + circle.ex["id"] + "</b>"
        fig.add_shape(
            type="circle",
            xref="x",
            yref="y",
            x0=x - r,
            y0=y - r,
            x1=x + r,
            y1=y + r,
            fillcolor=style_dict[label]["color"],
            line_color=style_dict[label]["color"],
            opacity=style_dict[label]["alpha"],
            line_width=2,
        )
        fig.add_annotation(
            x=x,
            y=y,
            xref="x",
            yref="y",
            text=label_text,
            showarrow=False,
            font=dict(
                size=font_size_calculator(label_text, r),
                color="white",
                family="Poppins, sans-serif",
            ),
            align="center",
        )
        if label_text != "<b>" + "..." + "</b>":
            fig.add_annotation(
                x=x,
                y=y
                - 0.1
                * style_dict[label]["scale_r"]
                * font_size_calculator(label_text, r)
                / 20,
                xref="x",
                yref="y",
                text=label_value,
                showarrow=False,
                font=dict(
                    size=font_size_calculator(label_text, r),
                    color="white",
                    family="Poppins, sans-serif",
                ),
                align="center",
            )

        i += 1

    fig.update_xaxes(range=[xmin, xmax])
    fig.update_yaxes(range=[ymin, ymax])
    fig.update_layout(
        # width=1000,
        # height=600,
        width=600,
        height=600,
        font=dict(color="white", family="Poppins, sans-serif"),
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        margin=dict(t=0, b=0, l=0, r=0),
        showlegend=True,
    )

    img_bytes = fig.to_image(format="png", scale=3)
    encoding = b64encode(img_bytes).decode()
    img_b64 = "data:image/png;base64," + encoding

    return img_b64, fig


def get_supply_breakdown_figure(allowed_tokens, df):

    fig = go.Figure()

    for allowed_token in allowed_tokens:
        col_name = f"carbonMetrics_{allowed_token['name']}Supply"
        fig.add_trace(
            go.Scatter(
                name=allowed_token["name"].upper(),
                x=df["carbonMetrics_datetime"],
                y=df[col_name],
                mode="lines",
                stackgroup="one",
                line={"width": 0.5, "color": allowed_token["color"]},
            )
        )

    fig.update_layout(
        height=300,
        font=GRAPH_FONT,
        xaxis_title="Date",
        yaxis_title="Supply",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=20, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
    )
    return fig


def get_polygon_retirement_breakdown_figure(df):

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["carbonMetrics_datetime"],
            y=df["carbonMetrics_totalKlimaRetirements"],
            mode="lines",
            name="Retired via KlimaDAO",
            stackgroup="one",
            line={"width": 0.5, "color": "#536C9C"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["carbonMetrics_datetime"],
            y=df["carbonMetrics_not_klima_retired"],
            mode="lines",
            name="Not Retired via KlimaDAO",
            stackgroup="one",
            line={"width": 0.5, "color": "#c74b0e"},
        )
    ),

    fig.update_layout(
        height=300,
        font=GRAPH_FONT,
        xaxis_title="Date",
        yaxis_title="Total Retirements",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=20, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
    )
    return fig


def get_eth_retirement_breakdown_figure(df):

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["carbonMetrics_datetime"],
            y=df["carbonMetrics_totalRetirements"],
            mode="lines",
            name="Not Retired by Klima",
            stackgroup="one",
            line={"width": 0.5, "color": "#c74b0e"},
        )
    )

    fig.update_layout(
        height=300,
        font=GRAPH_FONT,
        xaxis_title="Date",
        yaxis_title="Total Retirements",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=20, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
    )
    return fig


def total_carbon_supply_pie_chart(
    polygon_carbon_metrics_df, eth_carbon_metrics_df, celo_carbon_metrics_df
):
    labels = ["Polygon", "Ethereum", "Celo"]
    values = [
        polygon_carbon_metrics_df["carbonMetrics_totalCarbonSupply"].iloc[0],
        eth_carbon_metrics_df["carbonMetrics_totalCarbonSupply"].iloc[0],
        celo_carbon_metrics_df["carbonMetrics_totalCarbonSupply"].iloc[0],
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            textinfo="percent",
            textfont=dict(color="white", size=12),
            hoverlabel=dict(font_color="white", font_size=12),
            hole=0.3,
        )
    )
    fig.update_layout(
        height=360,
        paper_bgcolor=FIGURE_BG_COLOR,
        font_color="white",
        font_size=8,
        margin=dict(t=30, b=0, l=0, r=0),
        legend=dict(x=1, font=dict(size=12)),
    )
    fig.update_traces(textposition="inside")

    return fig


def pool_klima_retirement_chart_stacked(wrs):
    fig = go.Figure(data=[
        go.Bar(name='BCT', x=wrs['month_year_dt'], y=wrs['BCT_%']),
        go.Bar(name='MCO2', x=wrs['month_year_dt'], y=wrs['MCO2_%']),
        go.Bar(name='NBO', x=wrs['month_year_dt'], y=wrs['NBO_%']),
        go.Bar(name='NCT', x=wrs['month_year_dt'], y=wrs['NCT_%']),
        go.Bar(name='UBO', x=wrs['month_year_dt'], y=wrs['UBO_%'])
    ])

    fig.update_layout(
        barmode='stack',
        height=360,
        xaxis_title="Date",
        yaxis_title="Percentage",
        paper_bgcolor=FIGURE_BG_COLOR,
        plot_bgcolor=FIGURE_BG_COLOR,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=50, b=20, l=0, r=0),
        hovermode="x unified",
        hoverlabel=dict(font_color="white", font_size=8),
        font=GRAPH_FONT,
    )

    return fig


def pool_klima_retirement_table(summary_table):

    table = dash_table.DataTable(
        summary_table.to_dict('records'),
        [{"name": i,
          "id": i,
          "presentation": "markdown",
          "type": "text"} for i in summary_table.columns],
        style_header={"backgroundColor": GRAY,
                      "text-align": "center",
                      "color": WHITE,
                      "font_size": "10px",
                      "font-family": 'Inter, sans-serif',
                      "fontWeight": "bold"},
        style_data={
            "backgroundColor": DARK_GRAY,
            "color": WHITE,
            "font_size": "10px",
            "text-align": "center",
            'font-family': 'Inter, sans-serif'},
        style_table={
            "overflowX": "auto"}
    )
    return table
