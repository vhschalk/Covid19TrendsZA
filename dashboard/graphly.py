import datetime
import glob
import os
import copy

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot


def plots_rt():

    # Data

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_provincial_cumulative.csv'
    states_all_rt = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True)
    states_all_rt = states_all_rt.rename(columns={'date':'Date'})
    states_all_rt = states_all_rt.rename(columns={'state':'Province'})

    state_single = states_all_rt.query("Province == 'Total RSA'")


    # Simple Stats

    last = state_single.iloc[-1,:]['ML']
    latestrt = '%.2f'%last

    latestdate = state_single.iloc[-1,:]['Date']
    latestd = latestdate.strftime("%d %B %Y")


    # Graph 1

    state_single["e_plus"] = state_single['High_90'].sub(state_single['ML'])
    state_single["e_minus"] = state_single['ML'].sub(state_single['Low_90'])

    fig1 = px.line(state_single, x='Date', y='ML', color='Province',
              error_y='e_plus', error_y_minus='e_minus',
              title='Rt for Covid-19 in South Africa', line_shape='spline')
    fig1.update_traces(hovertemplate=None)
    fig1.update_layout(hovermode="x")

    plot_rt_country = plot(fig1, output_type='div', include_plotlyjs=False)


    # Graph 2

    states_rt = states_all_rt.query("Province != 'Total RSA'")

    grid_key = pd.DataFrame({'Province':['EC', 'FS', 'GP', 'KZN', 'LP', 'MP', 'NC', 'NW', 'WC'],
                          'Row':[1,1,1,2,2,2,3,3,3],
                          'Col':[1,2,3,1,2,3,1,2,3]})

    states_grid = states_rt.join(grid_key.set_index('Province'), on='Province')

    fig2 = px.line(states_grid, x='Date', y='ML', color='Province', facet_row='Row', facet_col='Col',
             title='Rt for Covid-19 in South African Provinces')
    fig2.update_traces(hovertemplate=None)
    fig2.update_layout(hovermode="x")

    plot_rt_states = plot(fig2, output_type='div', include_plotlyjs=False)


    return plot_rt_country, plot_rt_states, latestrt, latestd

def plots_data():

    # Setup common variables

    state_filter = list(state_key.keys())

    state_filter_i = copy.deepcopy(state_filter)
    state_filter_i.append('Date')

    colour_series = px.colors.qualitative.Vivid


    # Main data

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv'
    states_all_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True, index_col=0)
    states_all_i.tail()

    states_all = states_all_i.copy()
    states_all = states_all.reset_index()
    states_all = states_all.rename(columns={'date':'Date'})


    # Graph 1

    state_plot = states_all[state_filter_i]
    state_plotly = state_plot.melt(id_vars='Date', var_name='Province', value_name='Cases')

    fig1 = px.bar(state_plotly, title='Combined Cases Per Province', x='Date', y='Cases', color='Province',
                barmode='relative', color_discrete_sequence=colour_series)
    fig1.update_traces(hovertemplate=None)
    fig1.update_layout(hovermode="x")
    plot_combined_cases = plot(fig1, output_type='div', include_plotlyjs=False)


    # Graph 2

    states_all['Actual Data'] = states_all['total'].diff()

    smoothed = states_all['Actual Data'].rolling(7,
    win_type='gaussian',
    min_periods=1,
    center=True).mean(std=2).round()

    idx_start = np.searchsorted(smoothed, 25)

    smoothed = smoothed.iloc[idx_start:]
    states_all['Smoothed Data'] = smoothed

    daily = states_all[['Date','Actual Data','Smoothed Data']]

    daily_plotly = daily.melt(id_vars='Date', var_name='Range', value_name='Daily Cases')

    fig2 = px.line(daily_plotly, title='Daily Case Increase for South Africa',
                  x='Date', y='Daily Cases', color='Range', line_shape='spline')
    fig2.update_traces(hovertemplate=None)
    fig2.update_layout(hovermode="x")
    plot_daily_cases = plot(fig2, output_type='div', include_plotlyjs=False)


    # Graph 3

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_deaths.csv'
    states_all_deaths = pd.read_csv(url,
                        parse_dates=['date'], dayfirst=True,
                        squeeze=True,index_col=0).sort_index()
    state_deaths = states_all_deaths[state_filter]

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_recoveries.csv'
    states_all_recover = pd.read_csv(url,
                     parse_dates=['date'], dayfirst=True,
                     squeeze=True,index_col=0).sort_index()
    states_recover = states_all_recover[state_filter]

    states_series = pd.Series(states_all_i['total'].values, index=states_all_i.index.values, name='Cases')

    deaths_series = pd.Series(states_all_deaths['total'].values, index=states_all_deaths.index, name='Deaths')
    recover_series = pd.Series(states_all_recover['total'].values, index=states_all_recover.index, name='Recovered')

    states_combine = pd.concat([states_series, recover_series, deaths_series], axis=1)

    states_master = states_combine.ffill(axis=0)

    states_changed = states_master[['Recovered','Deaths']].sum(axis=1)

    active_all = states_master['Cases'].sub(states_changed)

    states_master['Active'] = active_all

    states_wide = states_master.reset_index(col_fill='Date')
    states_wide = states_wide.rename(columns={'index':'Date'})

    state_wide_plotly = states_wide.melt(id_vars='Date', var_name='Data', value_name='Count')

    fig3 = px.line(state_wide_plotly, x='Date', y='Count', color='Data',
              title='Covid-19 Data for South Africa', line_shape='spline')
    fig3.update_traces(hovertemplate=None)
    fig3.update_layout(hovermode="x")
    plot_stats = plot(fig3, output_type='div', include_plotlyjs=False)


    return plot_combined_cases, plot_daily_cases, plot_stats


state_key = {
    'EC':'Eastern Cape',
    'FS':'Free State',
    'GP':'Gauteng',
    'KZN':'Kwazulu Natal',
    'LP':'Limpopo',
    'MP':'Mpumalanga',
    'NC':'Northern Cape',
    'NW':'North-West',
    'WC':'Western Cape'
}
