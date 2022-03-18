import plotly.express as px
from .constants import FIGURE_BG_COLOR


def deposited_over_time(df):
    df = df.sort_values(by="Date", ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, font_color='white',
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=12,
                      margin=dict(t=0, b=0, l=0, r=0))
    return fig


def redeemed_over_time(df):
    df = df.sort_values(by="Date", ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, font_color='white',
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=12,
                      margin=dict(t=0, b=0, l=0, r=0))
    return fig
