from __future__ import annotations
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry
from collections import defaultdict
from .helpers import add_px_figure
from plotly.subplots import make_subplots
from .constants import FIGURE_BG_COLOR
import pandas as pd


def sub_plots_volume(df, last_df, title_indicator, title_graph, zero_evt_text):
    if not(df.empty) and (df["Quantity"].sum() != 0):
        fig = make_subplots(
            rows=2,
            cols=1,
            specs=[[{"type": "domain"}], [{"type": "xy"}]],
            subplot_titles=("", title_graph),
            vertical_spacing=0.1,
        )
        fig.update_layout(font_color='white', margin=dict(t=20, b=0, l=0, r=0))

        if not(last_df.empty) and (last_df["Quantity"].sum() != 0):
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=sum(df['Quantity']),
                title=dict(text=title_indicator, font=dict(size=12)),
                number=dict(suffix=" tCO2", font=dict(size=24)),
                delta={'position': "bottom", 'reference': sum(
                    last_df['Quantity']), 'relative': True, 'valueformat': '.1%'},
                domain={'x': [0.25, .75], 'y': [0.6, 1]}))
        else:
            fig.add_trace(go.Indicator(
                mode="number",
                value=sum(df['Quantity']),
                title=dict(text=title_indicator, font=dict(size=12)),
                number=dict(suffix=" tCO2", font=dict(size=24)),
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

        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(title_text="Date", showgrid=False),
                          yaxis=dict(title_text="Volume", showgrid=False), font_size=12,
                          hovermode='x unified', hoverlabel=dict(font_color='white', font_size=12),)
    else:
        fig = go.Figure()
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(visible=False), yaxis=dict(visible=False),
                          annotations=[dict(text=zero_evt_text,
                                            font=dict(color='white'), showarrow=False)])
    return fig


def sub_plots_vintage(df, last_df, title_indicator, title_graph, zero_evt_text):
    df = df[df["Vintage"] != "missing"].reset_index(drop=True)
    last_df = last_df[last_df["Vintage"] != "missing"].reset_index(drop=True)
    if not(df.empty):
        fig = make_subplots(
            rows=2,
            cols=1,
            specs=[[{"type": "domain"}], [{"type": "xy"}]],
            subplot_titles=("", title_graph),
            vertical_spacing=0.1,
        )
        fig.update_layout(font_color='white', margin=dict(t=20, b=0, l=0, r=0))
        if not(last_df.empty):
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=np.average(df['Vintage'], weights=df['Quantity']),
                number=dict(valueformat=".1f", font=dict(size=24)),
                delta={"reference": np.average(
                    last_df['Vintage'], weights=last_df['Quantity']), "valueformat": ".1f"},
                title=dict(text=title_indicator, font=dict(size=12)),
                domain={'x': [0.25, .75], 'y': [0.6, 1]}))
        else:
            fig.add_trace(go.Indicator(
                mode="number",
                value=np.average(df['Vintage'], weights=df['Quantity']),
                number=dict(valueformat=".1f", font=dict(size=24)),
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
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(title_text="Vintage", showgrid=False),
                          yaxis=dict(title_text="Volume", showgrid=False), font_size=12, hovermode='x unified',
                          hoverlabel=dict(font_color='white', font_size=12))
    else:
        fig = go.Figure()
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(visible=False), yaxis=dict(visible=False),
                          annotations=[dict(text=zero_evt_text,
                                            font=dict(color='white'), showarrow=False)])
    return fig


def map(df, zero_evt_text):
    df = df[df["Country"] != "missing"].reset_index(drop=True)
    if not(df.empty):
        country_index = defaultdict(str, {country: pycountry.countries.search_fuzzy(country)[
                                    0].alpha_3 for country in df.Country.astype(str).unique() if country != 'nan'})
        country_volumes = df.groupby('Country')['Quantity'].sum(
        ).sort_values(ascending=False).to_frame().reset_index()
        country_volumes['Country Code'] = [country_index[country]
                                           for country in country_volumes['Country']]
        country_volumes['text'] = country_volumes['Country Code'].astype(str)
        fig = px.choropleth(country_volumes, locations="Country Code",
                            color="Quantity",
                            hover_name='Country',
                            # hover_data=['text'],
                            # custom_data=['text'],
                            color_continuous_scale=px.colors.sequential.Plasma,
                            height=300)

        fig.update_layout(height=300, geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#4E5D6C',
                                               landcolor='darkgrey',
                                               subunitcolor='grey'),
                          font_color='white', dragmode=False, paper_bgcolor=FIGURE_BG_COLOR,  hovermode='x unified',
                          hoverlabel=dict(font_color='white', font_size=12), font_size=8,
                          margin=dict(t=0, b=0, l=0, r=0),
                          coloraxis_colorbar=dict(thickness=10, len=0.6))
    else:
        fig = go.Figure()
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(visible=False), yaxis=dict(visible=False),
                          annotations=[dict(text=zero_evt_text,
                                            font=dict(color='white'), showarrow=False)])
    return fig


def total_volume(df, title, zero_evt_text):
    if not(df.empty) and (df["Quantity"].sum() != 0):

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

        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(title_text="Date", showgrid=False),
                          yaxis=dict(title_text="Volume", showgrid=False),  hovermode='x unified',
                          hoverlabel=dict(font_color='white', font_size=12), font_size=12)
    else:
        fig = go.Figure()
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(visible=False), yaxis=dict(visible=False),
                          annotations=[dict(text=zero_evt_text,
                                            font=dict(color='white'), showarrow=False)])
    return fig


def total_vintage(df, zero_evt_text):
    df = df[df["Vintage"] != "missing"].reset_index(drop=True)
    if not(df.empty):
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
            title=dict(text="Average Credit Vintage (total)",
                       font=dict(size=12)),
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

        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(title_text="Vintage", showgrid=False),
                          yaxis=dict(title_text="Volume", showgrid=False),  hovermode='x unified',
                          hoverlabel=dict(font_color='white', font_size=12), font_size=12,
                          )
    else:
        fig = go.Figure()
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(visible=False), yaxis=dict(visible=False),
                          annotations=[dict(text=zero_evt_text,
                                            font=dict(color='white'), showarrow=False)])
    return fig


def methodology_volume(df, zero_evt_text):
    df = df[df['Methodology'] != "missing"].reset_index(drop=True)
    if not(df.empty):
        fig = px.bar(
            df.groupby('Methodology')[
                'Quantity'].sum().to_frame().reset_index(),
            x='Methodology',
            y='Quantity',
            title=''
        )
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(showgrid=False),
                          yaxis=dict(showgrid=False), font_color='white', hovermode='x unified',
                          hoverlabel=dict(font_color='white', font_size=12), font_size=8,
                          margin=dict(t=0, b=0, l=0, r=0))
    else:
        fig = go.Figure()
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(visible=False), yaxis=dict(visible=False),
                          annotations=[dict(text=zero_evt_text,
                                            font=dict(color='white'), showarrow=False)])
    return fig


def project_volume(df, zero_evt_text):
    df = df[df['Project Type'] != "missing"].reset_index(drop=True)
    if not(df.empty):
        fig = px.treemap(df, path=[px.Constant("All Projects"), 'Project Type', 'Country', 'Name'], values='Quantity',
                         hover_data=['Name', 'Quantity'],
                         color_discrete_sequence=px.colors.qualitative.Antique,
                         height=300, title='')
        fig.update_traces(textfont=dict(color='white'),
                          textinfo="label+value+percent parent+percent entry+percent root",
                          texttemplate='<br>'.join(['%{label}', 'Quantity=%{value}', '%{percentParent} of Parent',
                                                    '%{percentEntry} of Entry', '%{percentRoot} of Root']))
        fig.update_layout(paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, font=dict(color='white'),
                          hoverlabel=dict(font_color='white', font_size=8), font_size=12,
                          margin=dict(t=20, b=20, l=0, r=0))
    else:
        fig = go.Figure()
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(visible=False), yaxis=dict(visible=False),
                          annotations=[dict(text=zero_evt_text,
                                            font=dict(color='white'), showarrow=False)])
    return fig


def project_volume_mco2(df, zero_evt_text):
    df = df[df['Project Type'] != "missing"].reset_index(drop=True)
    if not(df.empty):
        fig = px.treemap(df, path=[px.Constant("All Projects"), 'Project Type', 'Name'], values='Quantity',
                         hover_data=['Name', 'Quantity'],
                         color_discrete_sequence=px.colors.qualitative.Antique,
                         height=300, title='')
        fig.update_traces(textfont=dict(color='white'),
                          textinfo="label+value+percent parent+percent entry+percent root",
                          texttemplate='<br>'.join(['%{label}', 'Quantity=%{value}', '%{percentParent} of Parent',
                                                    '%{percentEntry} of Entry', '%{percentRoot} of Root']))
        fig.update_layout(paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, font=dict(color='white'),
                          hoverlabel=dict(font_color='white', font_size=8), font_size=12,
                          margin=dict(t=20, b=20, l=0, r=0))
    else:
        fig = go.Figure()
        fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                          xaxis=dict(visible=False), yaxis=dict(visible=False),
                          annotations=[dict(text=zero_evt_text,
                                            font=dict(color='white'), showarrow=False)])
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
                      paper_bgcolor=FIGURE_BG_COLOR, font_color='white', font_size=8,
                      margin=dict(t=0, b=0, l=0, r=0),
                      legend=dict(x=1, font=dict(size=8)))
    fig.update_traces(textposition='inside')

    return fig


def bridges_pie_chart(bridges_info_dict):
    labels = list(bridges_info_dict.keys())
    values = [d['Tokenized Quantity'] for d in bridges_info_dict.values()]
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=values,  textinfo='percent', textfont=dict(
        color='white', size=12), hoverlabel=dict(font_color='white', font_size=12), hole=.3))
    fig.update_layout(height=300,
                      paper_bgcolor=FIGURE_BG_COLOR, font_color='white', font_size=8,
                      margin=dict(t=0, b=0, l=0, r=0),
                      legend=dict(x=1, font=dict(size=12)))
    fig.update_traces(textposition='inside')

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
                               paper_bgcolor=FIGURE_BG_COLOR, font_color='white', font_size=12,
                               margin=dict(t=0, b=0, l=0, r=0))
    return fig_eligible


def verra_vintage(df_verra, df_verra_toucan):
    df_verra_toucan_grouped = df_verra_toucan.groupby(
        'Vintage')['Quantity'].sum().to_frame().reset_index()
    df_verra_grouped = df_verra.groupby(
        'Vintage')['Quantity'].sum().to_frame().reset_index()
    df_verra_other_grouped = df_verra_grouped.merge(df_verra_toucan_grouped, how='left', left_on="Vintage",
                                                    right_on='Vintage', suffixes=('', '_Toucan'))
    df_verra_other_grouped['Quantity_Toucan'] = df_verra_other_grouped['Quantity_Toucan'].fillna(
        0)
    df_verra_other_grouped['Quantity'] = df_verra_other_grouped['Quantity'] - \
        df_verra_other_grouped['Quantity_Toucan']
    df_verra_other_grouped = df_verra_other_grouped[['Vintage', 'Quantity']]
    df_verra_other_grouped['Type'] = 'Rest of Issued VCU'
    df_verra_toucan_grouped['Type'] = 'Toucan Bridged Credit'
    df_other_and_toucan = pd.concat(
        [df_verra_toucan_grouped, df_verra_other_grouped]).reset_index()
    fig = px.bar(df_other_and_toucan, x="Vintage",
                 y="Quantity", color="Type", title="", height=300)
    fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_color='white', hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=12,
                      legend=dict(title="", orientation="h", yanchor="bottom",
                                  y=1.02, xanchor="right", x=1
                                  ))

    return fig


def verra_map(df_verra, df_verra_toucan):
    df_verra_toucan_grouped = df_verra_toucan.groupby(
        'Country')['Quantity'].sum().to_frame().reset_index()
    df_verra_grouped = df_verra.groupby(
        'Country')['Quantity'].sum().to_frame().reset_index()
    df_verra_grouped = df_verra_grouped.merge(df_verra_toucan_grouped, how='left', left_on="Country",
                                              right_on='Country', suffixes=('', '_Toucan'))
    df_verra_grouped['Quantity_Toucan'] = df_verra_grouped['Quantity_Toucan'].fillna(
        0)
    df_verra_grouped['Ratio'] = df_verra_grouped['Quantity_Toucan'] / \
        df_verra_grouped['Quantity']
    df_verra_grouped = df_verra_grouped[df_verra_grouped['Ratio'] != 0]
    df_verra_grouped['text'] = df_verra_grouped['Country'] + '<br>' + '<br>' + \
        'Tokenized Credits = ' + df_verra_grouped['Quantity_Toucan'].map('{:,.0f}'.format).astype(str) + '<br>' +\
        'Verra Issued Credits = ' + df_verra_grouped['Quantity'].map('{:,.0f}'.format).astype(str) + '<br>' +\
        'Ratio = ' + \
        df_verra_grouped['Ratio'].map('{:.4f}'.format).astype(str) + '<br>'
    df_verra_grouped = df_verra_grouped[df_verra_grouped["Country"] != ""].reset_index(
        drop=True)
    country_index = defaultdict(str, {country: pycountry.countries.search_fuzzy(country)[
                                0].alpha_3 for country in df_verra_grouped.Country.astype(str).unique()
        if country != 'nan'})
    df_verra_grouped['Country Code'] = [country_index[country]
                                        for country in df_verra_grouped['Country']]
    fig = px.choropleth(df_verra_grouped, locations="Country Code",
                        color="Ratio",
                        hover_name='Country',
                        custom_data=['text'],
                        color_continuous_scale=px.colors.diverging.Picnic,
                        height=300)

    fig.update_traces(hovertemplate="%{customdata}")

    fig.update_layout(height=300, geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#4E5D6C',
                                           landcolor='darkgrey',
                                           subunitcolor='grey'),
                      font_color='white', dragmode=False, paper_bgcolor=FIGURE_BG_COLOR,  hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=8), font_size=8,
                      margin=dict(t=50, b=0, l=0, r=0),
                      coloraxis_colorbar=dict(thickness=10, len=0.6))
    return fig


def verra_project(df_verra, df_verra_toucan):
    df_verra_toucan_grouped = df_verra_toucan.groupby(
        'Project Type')['Quantity'].sum().to_frame().reset_index()
    df_verra_grouped = df_verra.groupby(
        'Project Type')['Quantity'].sum().to_frame().reset_index()
    df_verra_other_grouped = df_verra_grouped.merge(df_verra_toucan_grouped, how='left', left_on="Project Type",
                                                    right_on='Project Type', suffixes=('', '_Toucan'))
    df_verra_other_grouped['Quantity_Toucan'] = df_verra_other_grouped['Quantity_Toucan'].fillna(
        0)
    df_verra_other_grouped['Quantity'] = df_verra_other_grouped['Quantity'] - \
        df_verra_other_grouped['Quantity_Toucan']
    df_verra_other_grouped['Type'] = 'Rest of Issued VCU'
    df_verra_toucan_grouped['Type'] = 'Toucan Bridged Credit'
    df_other_and_toucan = pd.concat(
        [df_verra_toucan_grouped, df_verra_other_grouped]).reset_index()
    fig = px.treemap(df_other_and_toucan, path=[px.Constant("All Projects"), 'Project Type', 'Type'], values='Quantity',
                     hover_data=['Type', 'Quantity'],
                     color_discrete_sequence=px.colors.qualitative.Antique,
                     height=300, title='')
    fig.update_traces(textfont=dict(color='white'), textinfo="label+value+percent parent+percent entry+percent root",
                      texttemplate='<br>'.join(['%{label}', 'Quantity=%{value}', '%{percentParent} of Parent',
                                                '%{percentEntry} of Entry', '%{percentRoot} of Root']))
    fig.update_layout(paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, font=dict(color='white'),
                      hoverlabel=dict(font_color='white', font_size=8), font_size=12,
                      margin=dict(t=20, b=20, l=0, r=0))

    return fig


def historical_prices(token_cg_dict, df_prices):
    fig = go.Figure()
    for i in token_cg_dict.keys():
        col_name = f"{i}_Price"
        filtered_df = df_prices[~df_prices[col_name].isna()]
        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df[col_name],
                                 mode='lines',
                                 name=i
                                 )
                      )
    fig.update_layout(height=300, font=dict(color='white'),
                      xaxis_title='Date', yaxis_title='Price',
                      paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, xaxis=dict(
                          showgrid=False), yaxis=dict(showgrid=False),
                      margin=dict(t=20, b=20, l=0, r=0),
                      hovermode='x unified', hoverlabel=dict(font_color='white', font_size=12))
    return fig


def pool_retired_chart(token_cg_dict, df_pool_retired):
    fig = go.Figure()
    for i in token_cg_dict.keys():
        pool_address = token_cg_dict[i]['address']
        filtered_df = df_pool_retired
        filtered_df[f'Quantity_{i}'] = filtered_df['Quantity']
        filtered_df.loc[filtered_df['Pool'] != pool_address, f'Quantity_{i}'] = 0
        filtered_df = filtered_df.sort_values(by="Date", ascending=True)
        filtered_df[f'Quantity_{i}'] = filtered_df[f'Quantity_{i}'].cumsum()
        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df[f'Quantity_{i}'],
                                 mode='lines',
                                 name=i,
                                 stackgroup='one'
                                 )
                      )
    fig.update_layout(height=300, font=dict(color='white'),
                      xaxis_title='Date', yaxis_title='Quantity',
                      paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, xaxis=dict(
                          showgrid=False), yaxis=dict(showgrid=False),
                      margin=dict(t=20, b=20, l=0, r=0),
                      hovermode='x unified', hoverlabel=dict(font_color='white', font_size=12))
    return fig


def on_vs_off_vintage(df_verra, bridges_info_dict):
    df_verra_grouped = df_verra.groupby(
        'Vintage')['Quantity'].sum().to_frame().reset_index()
    df_verra_other_grouped = pd.DataFrame()
    dfs = []
    for i in bridges_info_dict.keys():
        df = bridges_info_dict[i]["Dataframe"]
        df = df.groupby(
            'Vintage')['Quantity'].sum().to_frame().reset_index()
        df['Type'] = f'{i} Bridged Credits'
        dfs.append(df)
        if df_verra_other_grouped.empty:
            df_verra_other_grouped = df_verra_grouped.merge(df, how='left', left_on="Vintage",
                                                            right_on='Vintage', suffixes=('', f"_{i}"))
        else:
            df_verra_other_grouped = df_verra_other_grouped.merge(df, how='left', left_on="Vintage",
                                                                  right_on='Vintage', suffixes=('', f"_{i}"))
        df_verra_other_grouped[f'Quantity_{i}'] = df_verra_other_grouped[f'Quantity_{i}'].fillna(
            0)
        df_verra_other_grouped['Quantity'] = df_verra_other_grouped['Quantity'] - \
            df_verra_other_grouped[f'Quantity_{i}']
        df_verra_other_grouped = df_verra_other_grouped[[
            'Vintage', 'Quantity']]
        df_verra_other_grouped['Type'] = 'Rest of Issued VCU'

    df_other_and_bridges = pd.concat(
        dfs + [df_verra_other_grouped]).reset_index()
    fig = px.bar(df_other_and_bridges, x="Vintage",
                 y="Quantity", color="Type", title="", height=300)
    fig.update_layout(height=300, paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR,
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), font_color='white', hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=12), font_size=12,
                      legend=dict(title="", orientation="h", yanchor="bottom",
                                  y=1.02, xanchor="right", x=1
                                  ))

    return fig


def on_vs_off_map(df_verra, bridges_info_dict):
    df_verra_grouped = df_verra.groupby(
        'Country')['Quantity'].sum().to_frame().reset_index()
    df_verra_grouped["Text_Bridges"] = ""
    df_verra_grouped["Quantity_Bridges"] = 0
    for i in bridges_info_dict.keys():
        df = bridges_info_dict[i]["Dataframe"]
        df = df.groupby(
            'Country')['Quantity'].sum().to_frame().reset_index()
        df['Type'] = f'{i} Bridged Credit'
        df_verra_grouped = df_verra_grouped.merge(df, how='left', left_on="Country",
                                                  right_on='Country', suffixes=('', f"_{i}"))
        df_verra_grouped[f'Quantity_{i}'] = df_verra_grouped[f'Quantity_{i}'].fillna(
            0)
        df_verra_grouped["Quantity_Bridges"] = df_verra_grouped["Quantity_Bridges"] + \
            df_verra_grouped[f'Quantity_{i}']
        df_verra_grouped["Text_Bridges"] = df_verra_grouped["Text_Bridges"] + \
            f'{i} Bridged Credits = ' + \
            df_verra_grouped[f'Quantity_{i}'].map(
                '{:,.0f}'.format).astype(str) + '<br>'
    df_verra_grouped["Percentage"] = ((df_verra_grouped["Quantity_Bridges"] /
                                       df_verra_grouped['Quantity'])*100).round(decimals=4)
    df_verra_grouped['text'] = df_verra_grouped['Country'] + '<br>' + '<br>' + \
        df_verra_grouped["Text_Bridges"] + \
        'Total Tokenized Credits = ' + df_verra_grouped['Quantity_Bridges'].map('{:,.0f}'.format).astype(str) + \
        '<br>' +\
        'Verra Issued Credits = ' + df_verra_grouped['Quantity'].map('{:,.0f}'.format).astype(str) + '<br>' +\
        'Percentage = ' + \
        df_verra_grouped['Percentage'].astype(str) + '%' + '<br>'
    df_verra_grouped = df_verra_grouped[df_verra_grouped["Country"] != ""].reset_index(
        drop=True)
    country_index = defaultdict(str, {country: pycountry.countries.search_fuzzy(country)[
                                0].alpha_3 for country in df_verra_grouped.Country.astype(str).unique()
        if country != 'nan'})
    df_verra_grouped['Country Code'] = [country_index[country]
                                        for country in df_verra_grouped['Country']]

    cut_bins = [-np.inf, 0, 2, 5, 10, 100]
    bin_labels = ["0", "(0-2]", "(2-5]", "(5-10]", "(10-100]"]
    df_verra_grouped["Percentage Bins"] = pd.cut(
        df_verra_grouped["Percentage"], bins=cut_bins, labels=bin_labels)
    df_verra_grouped = df_verra_grouped.sort_values(by=["Percentage"])

    fig = px.choropleth(df_verra_grouped, locations="Country Code",
                        color="Percentage Bins",
                        hover_name='Country',
                        custom_data=['text'],
                        color_discrete_sequence=px.colors.sequential.Plasma_r,
                        height=300)

    fig.update_traces(hovertemplate="%{customdata}")

    fig.update_layout(height=300, geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#4E5D6C',
                                           landcolor='darkgrey',
                                           subunitcolor='grey'),
                      font_color='white', dragmode=False, paper_bgcolor=FIGURE_BG_COLOR,  hovermode='x unified',
                      hoverlabel=dict(font_color='white', font_size=8), font_size=8,
                      margin=dict(t=0, b=0, l=0, r=0),
                      legend=dict(font=dict(size=8), tracegroupgap=0,
                      title="Percentage <br>     Bins", y=0.5))
    return fig


def on_vs_off_project(df_verra, bridges_info_dict):
    df_verra_grouped = df_verra.groupby(
        'Project Type')['Quantity'].sum().to_frame().reset_index()
    df_verra_other_grouped = pd.DataFrame()
    dfs = []
    for i in bridges_info_dict.keys():
        df = bridges_info_dict[i]["Dataframe"]
        df = df.groupby(
            'Project Type')['Quantity'].sum().to_frame().reset_index()
        df['Type'] = f'{i} Bridged Credits'
        dfs.append(df)
        if df_verra_other_grouped.empty:
            df_verra_other_grouped = df_verra_grouped.merge(df, how='left', left_on="Project Type",
                                                            right_on='Project Type', suffixes=('', f"_{i}"))
        else:
            df_verra_other_grouped = df_verra_other_grouped.merge(df, how='left', left_on="Project Type",
                                                                  right_on='Project Type', suffixes=('', f"_{i}"))
        df_verra_other_grouped[f'Quantity_{i}'] = df_verra_other_grouped[f'Quantity_{i}'].fillna(
            0)
        df_verra_other_grouped['Quantity'] = df_verra_other_grouped['Quantity'] - \
            df_verra_other_grouped[f'Quantity_{i}']
        df_verra_other_grouped = df_verra_other_grouped[[
            'Project Type', 'Quantity']]
        df_verra_other_grouped['Type'] = 'Rest of Issued VCU'

    df_other_and_bridges = pd.concat(
        dfs + [df_verra_other_grouped]).reset_index()
    fig = px.treemap(df_other_and_bridges, path=[px.Constant("All Projects"), 'Project Type', 'Type'],
                     values='Quantity',
                     color_discrete_sequence=px.colors.qualitative.Antique,
                     hover_data=['Type', 'Quantity'],
                     height=300, title='')
    fig.update_traces(textfont=dict(color='white'), textinfo="label+value+percent parent+percent entry+percent root",
                      texttemplate='<br>'.join(['%{label}', 'Quantity=%{value}', '%{percentParent} of Parent',
                                                '%{percentEntry} of Entry', '%{percentRoot} of Root']))
    fig.update_layout(paper_bgcolor=FIGURE_BG_COLOR, plot_bgcolor=FIGURE_BG_COLOR, font=dict(color='white'),
                      hoverlabel=dict(font_color='white', font_size=8), font_size=12,
                      margin=dict(t=20, b=20, l=0, r=0))

    return fig
