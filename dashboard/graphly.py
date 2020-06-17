import datetime
import glob
import os
import copy, math
from datetime import timedelta

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot
from plotly.subplots import make_subplots


def plots_trends():

    # Setup common variables

    state_labels = list(state_key.values())


    # Data

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_provincial_cumulative.csv'
    states_all_rt = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True)
    states_all_rt = states_all_rt.rename(columns={'date':'Date'})
    states_all_rt = states_all_rt.rename(columns={'ML':'Rt'})
    states_all_rt = states_all_rt.rename(columns={'state':'Province'})

    state_single = states_all_rt.query("Province == 'Total RSA'")


    # Simple Stats

    latestresult = state_single.iloc[-1,:]
    rt = round(latestresult['Rt'], 2)
    latestrt = '%.2f'%rt

    d = latestresult['Date']
    latestd = d.strftime("%d %B %Y")


    # Graph 1

    state_single["e_plus"] = state_single['High_90'].sub(state_single['Rt'])
    state_single["e_minus"] = state_single['Rt'].sub(state_single['Low_90'])

    fig1 = px.line(state_single, x='Date', y='Rt', color='Province',
              error_y='e_plus', error_y_minus='e_minus',
              title='Rt for Covid-19 in South Africa', line_shape='spline')
    fig1.update_traces(hovertemplate=None)
    fig1.update_layout(hovermode="x")
    fig1['data'][0]['error_y']['color'] = 'lightblue'

    plot_rt_country = plot(fig1, output_type='div', include_plotlyjs=False)


    # Graph 2

    states_rt = states_all_rt.query("Province != 'Total RSA'")

    fig_px = px.line(states_rt, x='Date', y='Rt', color='Province')
    fig_len = len(fig_px['data'])

    fig2 = make_subplots(rows=3, cols=3,
                    subplot_titles=state_labels,
                    shared_xaxes=True, shared_yaxes=True)

    r = 0
    for p in range(fig_len):
        c = (p % 3) + 1
        if (c == 1):
            r+=1
        fig2.add_trace(fig_px['data'][p], row=r, col=c)

    fig2.update_layout(title_text="Rt for Covid-19 in South African Provinces", height=700)
    fig2.update_traces(hovertemplate=None)
    fig2.update_layout(hovermode="x")

    plot_rt_states = plot(fig2, output_type='div', include_plotlyjs=False)




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

    fig1 = px.bar(state_plotly, title='Total Cases Per Province', x='Date', y='Cases', color='Province',
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

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_recoveries.csv'
    states_all_recover = pd.read_csv(url,
                     parse_dates=['date'], dayfirst=True,
                     squeeze=True,index_col=0).sort_index()

    cases_series = pd.Series(states_all_i['total'].values, index=states_all_i.index.values, name='Cases')

    deaths_series = pd.Series(states_all_deaths['total'].values, index=states_all_deaths.index, name='Deaths')
    recover_series = pd.Series(states_all_recover['total'].values, index=states_all_recover.index, name='Recovered')

    states_combine = pd.concat([cases_series, recover_series, deaths_series], axis=1)

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


    # Future
    # Graph 4

    cases_df = cases_series.to_frame()
    cases_df = cases_df.reset_index()
    cases_df = cases_df.rename(columns={'index':'Date'})
    cases_df

    f = 60

    diff = cases_df['Cases'].diff()

    d = diff.values[-1]

    r_scenarios = [3.0, 2.0, 1.5, 1.0, 0.75, 0.5, 0.1]
    r_scenarios.append(rt)
    r_scenarios.sort(reverse=True)

    future_projections = None

    for r in r_scenarios:
        projection = cases_df.copy()
        lastd = cases_df['Date'].iloc[-1]
        lastc = cases_df['Cases'].iloc[-1]

        for i in range(f):
            lastd += timedelta(days=1)
            lastc = lastc + (d * r)

            calc = pd.DataFrame([[lastd, lastc]], columns=['Date', 'Cases'])
            # TODO: consider concat opertion here for faster processing
            projection = projection.append(calc)
            
        projection['Rt'] = r
        
        if future_projections is None:
            future_projections = projection
        else:
            future_projections = pd.concat([future_projections, projection])

        fig6 = px.line(future_projections, x='Date', y='Cases',
                animation_frame='Rt', height=600,
                title='Projected Convid-19 Cases Based for Different Rt Scenarios')
        fig6.update_layout(hovermode="x")
        plot_future = plot(fig6, output_type='div', include_plotlyjs=False)

    project = future_projections.query(f"Date == '{lastd}' and Rt == {rt}")['Cases'][0]
    future = math.trunc(project)


    # Simple Stats

    latestcases = states_wide.iloc[-1,:]
    latest = [latestcases['Cases'], latestcases['Recovered'], latestcases['Deaths'], latestcases['Active']]
    summary = [int(num) for num in latest]


    return plot_rt_country, plot_rt_states, latestrt, latestd, plot_combined_cases, plot_daily_cases, plot_stats, plot_future, summary, future


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

district_gp_key = {
'ekurhuleni':'Ekurhuleni',
'johannesburg':'Johannesburg',
'tshwane':'Tshwane'
}

district_wc_key = {
'CT':'City of Cape Town (D)',
'CT-WE':'Western',
'CT-SO':'Southern Suburbs',
'CT-NO':'Northern Suburbs',
'CT-TB':'Tygerberg',
'CT-EA':'Eastern',
'CT-KF':'Klipfontein',
'CT-MP':'Mitchells Plain',
'CT-KL':'Khayelitsha',
'CW':'Cape Winelands (D)',
'CW-BV':'Breede Valley',
'CW-DS':'Drakenstein',
'CW-LB':'Langeberg',
'CW-SB':'Stellenbosch',
'CW-WB':'Witzenberg',
'CK':'Central Karoo (D)',
'CK-BW':'Beaufort West',
'CK-LB':'Laingsburg',
'CK-PA':'Prince Albert',
'GR':'Eden (D)',
'GR-BT':'Bitou',
'GR-GE':'George',
'GR-HQ':'Hessequa',
'GR-KL':'Kannaland',
'GR-KN':'Knysna',
'GR-MB':'Mossel Bay',
'GR-OS':'Oudtshoorn',
'OB':'Overberg (D)',
'OB-CA':'Cape Agulhas',
'OB-OS':'Overstrand',
'OB-SD':'Swellendam',
'OB-TK':'Theewaterskloof',
'WC':'West Coast (D)',
'WC-BR':'Bergrivier',
'WC-CB':'Cederberg',
'WC-MZ':'Matzikama',
'WC-SB':'Saldanha Bay',
'WC-SL':'Swartland'
}