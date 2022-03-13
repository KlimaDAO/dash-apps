import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry
from collections import defaultdict
from .helpers import add_px_figure
from plotly.subplots import make_subplots
from .colors import colors


def sub_plots_volume(df, last_df, title_indicator, title_graph):
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "domain"}], [{"type": "xy"}]],
        subplot_titles=("", title_graph),
        vertical_spacing=0.1,
    )

    fig.update_layout(font_color='white', margin=dict(t=20, b=0, l=0, r=0))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=sum(df['Quantity']),
        title=dict(text=title_indicator, font=dict(size=12)),
        number=dict(suffix=" tCO2", font=dict(size=24)),
        delta={'position': "bottom", 'reference': sum(
            last_df['Quantity']), 'relative': True, 'valueformat': '.1%'},
        domain={'x': [0.25, .75], 'y': [0.6, 1]}))

    add_px_figure(
        px.bar(
            df.groupby("Date")['Quantity'].sum().reset_index(),
            x="Date",
            y="Quantity",
            title=title_graph,
        ),
        fig,
        row=2, col=1)

    fig.update_layout(height=300, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'],
                      xaxis=dict(title_text="Date", showgrid=False),
                      yaxis=dict(title_text="Volume", showgrid=False), font_size=12,
                      hovermode='x unified', hoverlabel=dict(font_color='white', font_size=12),)
    return fig


def sub_plots_vintage(df, last_df, title_indicator, title_graph):
    df = df[df["Vintage"] != ""].reset_index(drop=True)
    last_df = last_df[last_df["Vintage"] != ""].reset_index(drop=True)
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "domain"}], [{"type": "xy"}]],
        subplot_titles=("", title_graph),
        vertical_spacing=0.1,
    )
    fig.update_layout(font_color='white', margin=dict(t=20, b=0, l=0, r=0))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=np.average(df['Vintage'], weights=df['Quantity']),
        number=dict(valueformat=".1f", font=dict(size=24)),
        delta={"reference": np.average(
            last_df['Vintage'], weights=last_df['Quantity']), "valueformat": ".1f"},
        title=dict(text=title_indicator, font=dict(size=12)),
        domain={'x': [0.25, .75], 'y': [0.6, 1]}))

    add_px_figure(
        px.bar(
            df.groupby('Vintage')[
                'Quantity'].sum().to_frame().reset_index(),
            x='Vintage',
            y='Quantity',
            title=title_graph
        ),
        fig,
        row=2, col=1
    )
    fig.update_layout(height=300, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'],
                      xaxis=dict(title_text="Vintage", showgrid=False),
                      yaxis=dict(title_text="Volume", showgrid=False), font_size=12, hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12))

    return fig


def map(df, title):
    df = df[df["Country"] != ""].reset_index(drop=True)
    country_index = defaultdict(str, {country: pycountry.countries.search_fuzzy(country)[
                                0].alpha_3 for country in df.Region.astype(str).unique() if country != 'nan'})
    country_volumes = df.groupby('Country')['Quantity'].sum(
    ).sort_values(ascending=False).to_frame().reset_index()
    country_volumes['Country Code'] = [country_index[country]
                                       for country in country_volumes['Country']]
    fig = px.choropleth(country_volumes, locations="Country Code",
                        color="Quantity",
                        hover_name='Country',
                        color_continuous_scale=px.colors.sequential.Plasma,
                        height=600)

    fig.update_layout(height=300, geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#4E5D6C',
                                           landcolor='darkgrey',
                                           subunitcolor='grey'), title=dict(
        text=title,
        x=0.5, font=dict(
            color=colors['kg_color_sub2'],
            size=24)),
        font_color='white', dragmode=False, paper_bgcolor=colors['bg_color'],  hovermode='x unified',
        hoverlabel=dict(font_color='white', font_size=12), font_size=12,
        margin=dict(t=50, b=0, l=0, r=0))
    return fig


def total_volume(df, title):
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "domain"}], [{"type": "xy"}]],
        vertical_spacing=0.1,
        subplot_titles=("", "")
    )
    fig.update_layout(font_color='white', margin=dict(t=20, b=0, l=0, r=0))

    fig.add_trace(go.Indicator(
        mode="number",
        value=sum(df['Quantity']),
        title=dict(text=title, font=dict(size=12)),
        number=dict(suffix=" tCO2", font=dict(size=24)),
        domain={'x': [0.25, .75], 'y': [0.6, 1]}))

    add_px_figure(
        px.bar(
            df.groupby("Date")['Quantity'].sum().reset_index(),
            x="Date",
            y="Quantity",
            title=""
        ),
        fig,
        row=2, col=1)

    fig.update_layout(height=300, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'],
                      xaxis=dict(title_text="Date", showgrid=False),
                      yaxis=dict(title_text="Volume", showgrid=False),  hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=12)
    return fig


def total_vintage(df):
    df = df[df["Vintage"] != ""].reset_index(drop=True)
    df = df[~df["Vintage"].isna()].reset_index(drop=True)
    value = np.average(df['Vintage'], weights=df['Quantity'])
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "domain"}], [{"type": "xy"}]],
        vertical_spacing=0.1,
        subplot_titles=("", "")
    )
    fig.update_layout(font_color='white', margin=dict(t=20, b=0, l=0, r=0))

    fig.add_trace(go.Indicator(
        mode="number",
        value=value,
        number=dict(valueformat=".1f", font=dict(size=24)),
        title=dict(text="Average Credit Vintage (total)", font=dict(size=12)),
        domain={'x': [0.25, .75], 'y': [0.6, 1]}))
    add_px_figure(
        px.bar(
            df.groupby('Vintage')[
                'Quantity'].sum().to_frame().reset_index(),
            x='Vintage',
            y='Quantity',
            title=''
        ),
        fig,
        row=2, col=1
    )

    fig.update_layout(height=300, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'],
                      xaxis=dict(title_text="Vintage", showgrid=False),
                      yaxis=dict(title_text="Volume", showgrid=False),  hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=12,
                      )
    return fig


def methodology_volume(df):
    df = df[df['Methodology'] != ""].reset_index(drop=True)
    fig = px.bar(
        df.groupby('Methodology')['Quantity'].sum().to_frame().reset_index(),
        x='Methodology',
        y='Quantity',
        title=''
    )
    fig.update_layout(height=300, paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'],
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_color='white', hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=8)
    return fig


def project_volume(df):
    fig = px.treemap(df, path=[px.Constant("All Projects"), 'Project Type', 'Country', 'Name'], values='Quantity',
                     hover_data=['Name', 'Quantity'],
                     height=300, title='')
    fig.update_traces(textfont=dict(color='white'), textinfo="label+value+percent parent+percent entry+percent root",
                      texttemplate='<br>'.join(['%{label}', 'Quantity=%{value}', '%{percentParent} of Parent',
                                                '%{percentEntry} of Entry', '%{percentRoot} of Root']))
    fig.update_layout(paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'], font=dict(color='white'),
                      hoverlabel=dict(font_color='white', font_size=12), font_size=12,
                      margin=dict(t=20, b=20, l=0, r=0))
    return fig


def pool_pie_chart(df):
    labels = ['BCT', 'NCT', 'Not Pooled']
    BCT = df['BCT Quantity'].sum()
    NCT = df['NCT Quantity'].sum()
    TCO2 = df['Total Quantity'].sum()-BCT-NCT
    values = [BCT, NCT, TCO2]
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=values,  textinfo='percent', textfont=dict(
        color='white', size=12), hoverlabel=dict(font_color='white', font_size=12), hole=.3))
    fig.update_layout(height=300,
                      paper_bgcolor=colors['bg_color'], font_color='white', font_size=12,
                      margin=dict(t=0, b=0, l=0, r=0))

    return fig


def eligible_pool_pie_chart(df, pool_key):
    if pool_key == "BCT":
        df = df[df["Vintage"] >= 2008].reset_index()
    elif pool_key == "NCT":
        df = df[df["Vintage"] >= 2012].reset_index()
    labels = [pool_key, f'NON_{pool_key}']
    BCT = df[f'{pool_key} Quantity'].sum()
    Non_BCT = df['Total Quantity'].sum() - BCT
    values = [BCT, Non_BCT]
    fig_eligible = go.Figure()
    fig_eligible.add_trace(go.Pie(labels=labels, values=values,  textinfo='percent', textfont=dict(
        color='white', size=12), hoverlabel=dict(font_color='white', font_size=12), hole=.3))
    fig_eligible.update_traces(marker=dict(colors=['red', 'green']))

    fig_eligible.update_layout(height=300,
                               paper_bgcolor=colors['bg_color'], font_color='white', font_size=12,
                               margin=dict(t=0, b=0, l=0, r=0))
    return fig_eligible
