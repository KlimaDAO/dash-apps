import plotly.express as px
from .constants import FIGURE_BG_COLOR, GRAPH_FONT
from src.apps.services import Offsets


def stats_over_time(bridge, pool, status):
    date_column = Offsets.status_date_column(status)
    offsets = Offsets().filter(bridge, pool, status).sum_over_time(date_column, "Quantity", "daily")
    offsets["Date"] = offsets[date_column]
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
