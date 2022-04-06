import plotly.express as px
from .constants import FIGURE_BG_COLOR
import plotly.graph_objects as go


def deposited_over_time(df):
    df = df.sort_values(by="Date", ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, font_color='white',
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=8,
                      margin=dict(t=0, b=0, l=0, r=0))
    return fig


def redeemed_over_time(df):
    df = df.sort_values(by="Date", ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, font_color='white',
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=8,
                      margin=dict(t=0, b=0, l=0, r=0))
    return fig


def retired_over_time(pool_address, pool_name, df_pool_retired):
    fig = go.Figure()
    filtered_df = df_pool_retired
    filtered_df[f'Quantity_{pool_name}'] = filtered_df['Quantity']
    filtered_df.loc[filtered_df['Pool'] !=
                    pool_address, f'Quantity_{pool_name}'] = 0
    filtered_df = filtered_df.sort_values(by="Date", ascending=True)
    filtered_df[f'Quantity_{pool_name}'] = filtered_df[f'Quantity_{pool_name}'].cumsum(
    )
    fig = px.area(filtered_df, x="Date", y=f'Quantity_{pool_name}')
    fig.update_layout(height=300, font=dict(color='white'),
                      xaxis_title='Date', yaxis_title='Quantity',
                      paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, xaxis=dict(
        showgrid=False), yaxis=dict(showgrid=False), font_size=8,
        margin=dict(t=20, b=20, l=0, r=0),
        hovermode='x unified', hoverlabel=dict(font_color='white', font_size=12))
    return fig
