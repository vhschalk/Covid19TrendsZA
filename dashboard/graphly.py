import datetime
import glob
import os
import copy, math
from datetime import timedelta, date

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot
from plotly.subplots import make_subplots

# Change to avoid temporary delays
repo = 'dsfsi' #dsfsi 

def trend_plots():

    # Setup common variables

    content_trend = {}

    state_labels = list(state_key.values())


    # Rt mode 1
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_provincial_cumulative.csv'
    states_all_rt_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True, index_col=[0,1])

    states_all_rt = states_all_rt_i.copy()
    states_all_rt = states_all_rt.reset_index()
    states_all_rt = states_all_rt.rename(columns={'date':'Date'})
    states_all_rt = states_all_rt.rename(columns={'ML':'Rt'})
    states_all_rt = states_all_rt.rename(columns={'state':'Province'})


    # Rt model 2
    
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_mcmc.csv'
    state_rt_mcmc = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True)
    state_rt_mcmc = state_rt_mcmc.rename(columns={'date':'Date'})
    state_rt_mcmc = state_rt_mcmc.rename(columns={'Median':'Rt'})


    # Rt model 1 summary
    X0rt1 = state_rt_mcmc.iloc[0]['Date'] # for improved start range

    latest_result_rt = states_all_rt.iloc[-1]
    X2rt1 = latest_result_rt['Date']
    latest_d_rt1 = X2rt1.strftime("%d %B %Y")

    rt1_last_df = states_all_rt_i.groupby(level=0)[['ML']].last()
    rt1_states = rt1_last_df['ML'].to_dict()


    # Rt modcel 2 summary

    X0rt2 = state_rt_mcmc.iloc[0,:]['Date']

    latest_rt2 = state_rt_mcmc.iloc[-1]
    rt2 = round(latest_rt2['Rt'], 2)

    X2rt2 = latest_rt2['Date']
    latest_d_rt2 = X2rt2.strftime("%d %B %Y")


    # Plot: Model 1: Rt for Covid-19 in South Africa

    state_rt_mcmc["e_plus"] = state_rt_mcmc['High_80'].sub(state_rt_mcmc['Rt'])
    state_rt_mcmc["e_minus"] = state_rt_mcmc['Rt'].sub(state_rt_mcmc['Low_80'])

    fig_rt2 = px.line(state_rt_mcmc, x='Date', y='Rt',
                error_y='e_plus', error_y_minus='e_minus',
                title='Model V2: Rt for Covid-19 in South Africa', line_shape='spline')
    fig_rt2.update_traces(hovertemplate=None)
    fig_rt2.update_layout(hovermode="x")
    fig_rt2['data'][0]['error_y']['color'] = 'lightblue'

    fig_rt2.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=X0rt2,
        y0=1,
        x1=X2rt2,
        y1=1,
        opacity=0.6,
        line=dict(
            color="Crimson",
            width=2,
            dash='dash'
    ))

    plot_rt_country = plot(fig_rt2, output_type='div', include_plotlyjs=False)


    # Plot: Model 1: Rt for Covid-19 in South African provinces

    states_rt = states_all_rt.query("Province != 'Total RSA'")

    fig_px = px.line(states_rt, x='Date', y='Rt', color='Province')
    fig_len = len(fig_px['data'])

    fig_rt_province = make_subplots(rows=3, cols=3,
                    subplot_titles=state_labels,
                    shared_xaxes=True, shared_yaxes=True)

    r = 0
    for p in range(fig_len):
        c = (p % 3) + 1
        if (c == 1):
            r+=1
        fig_rt_province.add_trace(fig_px['data'][p], row=r, col=c)
        
        fig_rt_province.add_shape(
        type="line",
        xref="x{0}".format(p+1),
        yref="y{0}".format(p+1),
        x0=X0rt1,
        y0=1,
        x1=X2rt1,
        y1=1,
        opacity=0.6,
        line=dict(
            color="Crimson",
            width=2,
            dash='dash'
        ))

    fig_rt_province.update_layout(title_text="Model V1: Rt for Covid-19 in South African Provinces", height=700)
    fig_rt_province.update_traces(hovertemplate=None)
    fig_rt_province.update_layout(hovermode="x")

    plot_rt_states = plot(fig_rt_province, output_type='div', include_plotlyjs=False)




    # Setup common variables

    state_filter = list(state_key.keys())

    state_filter_i = copy.deepcopy(state_filter)
    state_filter_i.append('Date')

    colour_series = px.colors.qualitative.Vivid


    # Main data

    url = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv'
    states_all_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True, index_col=0)
    states_all_i.tail()

    states_all = states_all_i.copy()
    states_all = states_all.reset_index()
    states_all = states_all.rename(columns={'date':'Date'})


    # Graph 3

    state_plot = states_all[state_filter_i]
    state_plotly = state_plot.melt(id_vars='Date', var_name='Province', value_name='Cases')

    fig1 = px.bar(state_plotly, title='Total Cases Per Province', x='Date', y='Cases', color='Province',
                barmode='relative', color_discrete_sequence=colour_series)
    fig1.update_traces(hovertemplate=None)
    fig1.update_layout(hovermode="x")
    plot_combined_cases = plot(fig1, output_type='div', include_plotlyjs=False)


    # Graph 4

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


    # Graph 5

    url = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/covid19za_provincial_cumulative_timeline_deaths.csv'
    states_all_deaths = pd.read_csv(url,
                        parse_dates=['date'], dayfirst=True,
                        squeeze=True,index_col=0).sort_index()

    url = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/covid19za_provincial_cumulative_timeline_recoveries.csv'
    states_all_recover = pd.read_csv(url,
                     parse_dates=['date'], dayfirst=True,
                     squeeze=True,index_col=0).sort_index()

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_timeline_testing.csv'
    states_all_tests = pd.read_csv(url, parse_dates=['date'], dayfirst=True, index_col=0)
    states_all_tests.tail()

    casezero = states_all_i.index[0]
    caselast = states_all_i.index[-1]

    tests_series = states_all_tests.loc[casezero:caselast]['cumulative_tests']

    cases_series = pd.Series(states_all_i['total'].values, index=states_all_i.index.values, name='Cases')

    deaths_series = pd.Series(states_all_deaths['total'].values, index=states_all_deaths.index, name='Deaths')
    recover_series = pd.Series(states_all_recover['total'].values, index=states_all_recover.index, name='Recovered')

    states_combine = pd.concat([cases_series, recover_series, deaths_series, tests_series], axis=1)
    states_combine = states_combine.rename(columns={'cumulative_tests':'Tests'})
    states_combine.loc[casezero,'Tests'] = 163
    states_master = states_combine.ffill(axis=0)

    states_changed = states_master[['Recovered','Deaths']].sum(axis=1)

    active_all = states_master['Cases'].sub(states_changed)

    states_master['Active'] = active_all

    states_wide = states_master.reset_index(col_fill='Date')
    states_wide = states_wide.rename(columns={'index':'Date'})

    state_wide_plotly = states_wide.melt(id_vars='Date', var_name='Data', value_name='Count')

    px_data_sa = px.line(state_wide_plotly, x='Date', y='Count', color='Data', line_shape='spline')
    fig_data_sa = make_subplots(specs=[[{"secondary_y": True}]])

    fig_data_sa.add_trace(px_data_sa['data'][0], secondary_y=True)
    fig_data_sa.add_trace(px_data_sa['data'][1], secondary_y=True)
    fig_data_sa.add_trace(px_data_sa['data'][2], secondary_y=True)
    fig_data_sa.add_trace(px_data_sa['data'][4], secondary_y=True)
    fig_data_sa.add_trace(px_data_sa['data'][3], secondary_y=False)

    fig_data_sa.update_yaxes(title_text="Rest of Data", secondary_y=True)
    fig_data_sa.update_yaxes(title_text="Tests", secondary_y=False)
    fig_data_sa.update_layout(title="Covid-19 Data for South Africa")

    fig_data_sa.update_traces(hovertemplate=None)
    fig_data_sa.update_layout(hovermode="x")

    plot_stats = plot(fig_data_sa, output_type='div', include_plotlyjs=False)


    # Stats

    latestcases = states_wide.iloc[-1]
    a = latestcases['Cases']
    a = format_comma(a)

    b = latestcases['Recovered']
    b = format_comma(b)

    c = latestcases['Deaths']
    c = format_comma(c)

    d = latestcases['Active']
    d = format_comma(d)

    e = latestcases['Tests']
    e = format_comma(e)

    latest = latestcases['Date']
    latest_date = latest.strftime("%d %B %Y")
    

    content_trend['plot_rt_country'] = plot_rt_country
    content_trend['plot_rt_states'] = plot_rt_states
    content_trend['latest_rt'] = rt2
    content_trend['latest_rt2date'] = latest_d_rt2
    content_trend['rt_ec'] = rt1_states['EC']
    content_trend['rt_fs'] = rt1_states['FS']
    content_trend['rt_gp'] = rt1_states['GP']
    content_trend['rt_kzn'] = rt1_states['KZN']
    content_trend['rt_lp'] = rt1_states['LP']
    content_trend['rt_mp'] = rt1_states['MP']
    content_trend['rt_nc'] = rt1_states['NC']
    content_trend['rt_nw'] = rt1_states['NW']
    content_trend['rt_wc'] = rt1_states['WC']
    content_trend['latest_rt1date'] = latest_d_rt1
    content_trend['plot_combined_cases'] = plot_combined_cases
    content_trend['plot_daily_cases'] = plot_daily_cases
    content_trend['plot_stats'] = plot_stats
    content_trend['cases'] = a
    content_trend['recovered'] = b
    content_trend['deaths'] = c
    content_trend['active'] = d
    content_trend['tests'] = e
    content_trend['latest_date'] = latest_date

    return content_trend


def future_plots():

    # Setup common variables

    content_future = {}


    # Rt model 2

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_mcmc.csv'
    state_rt_mcmc = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True)

    latest_rt2 = state_rt_mcmc.iloc[-1]
    rt2 = round(latest_rt2['Median'], 2)
    

    # Herd immunity

    #url = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/district_data/za_province_pop.csv'
    #province_pops = pd.read_csv(url, header=None, names=['Province','Pop'])
    #country_pop = province_pops['Pop'].sum()
    country_pop = 58775020

    Pc = 1-(1/rt2)
    immune = country_pop * Pc
    future_immune = format_comma(immune)
    

    url = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv'
    states_all_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True, index_col=0)
    states_all_i.tail()

    states_all = states_all_i.copy()
    states_all = states_all.reset_index()
    states_all = states_all.rename(columns={'date':'Date'})

    cases_series = pd.Series(states_all_i['total'].values, index=states_all_i.index.values, name='Cases')


    # Forecast Calc

    cases_df = cases_series.to_frame()
    cases_df = cases_df.reset_index()
    cases_df = cases_df.rename(columns={'index':'Date'})
    cases_df

    f = 60
    f2 = 30

    diff = cases_df['Cases'].diff()

    d = diff.values[-1]

    r_scenarios = [1.5, 1.4, 1.3, 1.25, 1.2, 1.15, 1.1, 1.075, 1.05, 1.025, 1.0, 0.975, 0.95, 0.925, 0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.25, 0.1]
    if (rt2 not in r_scenarios):
        r_scenarios.append(rt2)
        r_scenarios.sort(reverse=True)

    future_projections = None

    for r in r_scenarios:
        projection = cases_df.copy()
        lastd = cases_df['Date'].iloc[-1]
        lastc = cases_df['Cases'].iloc[-1]
        d = diff.values[-1]

        for i in range(f):
            lastd += timedelta(days=1)
            newc = lastc + (d * r)
            d = newc - lastc
            lastc = newc

            calc = pd.DataFrame([[lastd, lastc]], columns=['Date', 'Cases'])
            # TODO: consider concat opertion here for faster processing
            projection = projection.append(calc)
            
        projection['R'] = r
        
        if future_projections is None:
            future_projections = projection
        else:
            future_projections = pd.concat([future_projections, projection])


    # Simple Stats

    current_forecast = future_projections.query(f"R == {rt2}")
    last_forecast = current_forecast.iloc[-1]
    future_f = math.trunc(last_forecast['Cases'])
    future = format_comma(future_f)

    infected = future_f / country_pop * 100
    future_perc = f'{infected:.1f}%'


    Xdt = date.today()
    X0f = current_forecast.iloc[0]['Date']
    X1f = Xdt + timedelta(days=f2)
    X2f = last_forecast['Date']

    max_forecast = max(current_forecast['Cases']) * 1.05
    max_country = country_pop * 1.1
    max_future = min(max_forecast, max_country)


    # Graph 1

    fig6 = px.line(current_forecast, x='Date', y='Cases',
                range_y=[0, max_future],
                title='Covid-19 Cases Forecast for Current Rt')
    fig6.update_traces(hovertemplate=None)
    fig6.update_layout(hovermode="x")

    fig6.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=Xdt,
        y0=0,
        x1=Xdt,
        y1=max_future,
        opacity=0.6,
        line=dict(
            color="Black",
            width=2,
            dash='dashdot'
    ))

    fig6.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=X0f,
        y0=immune,
        x1=X2f,
        y1=immune,
        opacity=0.6,
        line=dict(
            color="Crimson",
            width=2,
            dash='dash'
    ))

    fig6.add_annotation(
                x=X1f,
                y=immune * 1.05,
                text="Herd Immunity",
                showarrow=False
    )

    plot_forecast = plot(fig6, output_type='div', include_plotlyjs=False)

    
    # Graph 2

    increasing_forecast = future_projections.query(f"R > 1")

    fig7 = px.line(increasing_forecast, x='Date', y='Cases',
               animation_frame='R', height=600, range_y=[0, max_country],
               title='Covid-19 Cases Forecast for Increasing Cases (Rt is bigger than 1)')
    fig7.update_layout(hovermode="x")

    plot_scenarios1 = plot(fig7, output_type='div', include_plotlyjs=False, auto_play=False)


    # Graph 3

    linear_forecast = future_projections.query(f"R == 1")
    max_linear = max(linear_forecast['Cases'])

    fig8 = px.line(linear_forecast, x='Date', y='Cases',
                range_y=[0, max_linear],
                title='Covid-19 Cases Forecast for Increasing Cases (Rt is 1)')
    fig8.update_traces(hovertemplate=None)
    fig8.update_layout(hovermode="x")

    fig8.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=Xdt,
        y0=0,
        x1=Xdt,
        y1=max_linear,
        opacity=0.6,
        line=dict(
            color="Black",
            width=2,
            dash='dashdot'
    ))

    plot_scenarios2 = plot(fig8, output_type='div', include_plotlyjs=False, auto_play=False)


    # Graph 4

    decline_forecast = future_projections.query(f"R < 1")
    max_decline = max(decline_forecast['Cases']) * 1.05

    fig9 = px.line(decline_forecast, x='Date', y='Cases',
               animation_frame='R', height=600, range_y=[0, max_decline],
               title='Covid-19 Cases Forecast for Decreasing Cases (Rt is less than 1)')
    fig9.update_traces(hovertemplate=None)
    fig9.update_layout(hovermode="x")

    fig9.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=Xdt,
        y0=0,
        x1=Xdt,
        y1=max_decline,
        opacity=0.6,
        line=dict(
            color="Black",
            width=2,
            dash='dashdot'
    ))

    plot_scenarios3 = plot(fig9, output_type='div', include_plotlyjs=False, auto_play=False)


    content_future['latest_rt'] = rt2
    content_future['future_cases'] = future
    content_future['future_perc'] = future_perc
    content_future['future_immune'] = future_immune
    content_future['plot_forecast'] = plot_forecast
    content_future['plot_scenarios1'] = plot_scenarios1
    content_future['plot_scenarios2'] = plot_scenarios2
    content_future['plot_scenarios3'] = plot_scenarios3

    return content_future


def format_comma(num):
    return f'{num:,.0f}'


def rt_model1():

    # Rt mode 1
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_provincial_cumulative.csv'
    states_all_rt_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True, index_col=[0,1])

    states_all_rt = states_all_rt_i.copy()
    states_all_rt = states_all_rt.reset_index()
    states_all_rt = states_all_rt.rename(columns={'date':'Date'})
    states_all_rt = states_all_rt.rename(columns={'ML':'Rt'})
    states_all_rt = states_all_rt.rename(columns={'state':'Province'})

    state_single = states_all_rt.query("Province == 'Total RSA'")

    state_single["e_plus"] = state_single['High_90'].sub(state_single['Rt'])
    state_single["e_minus"] = state_single['Rt'].sub(state_single['Low_90'])

    X0rt1 = state_single.iloc[0]['Date']
    latest_result_rt = state_single.iloc[-1]
    X2rt1 = latest_result_rt['Date']
    rt1 = latest_result_rt['Rt']

    latest_d_rt1 = X2rt1.strftime("%d %B %Y")

    fig_rt1 = px.line(state_single, x='Date', y='Rt',
                error_y='e_plus', error_y_minus='e_minus',
                title='Model 1: Rt for Covid-19 in South Africa', line_shape='spline')
    fig_rt1.update_traces(hovertemplate=None)
    fig_rt1.update_layout(hovermode="x")
    fig_rt1['data'][0]['error_y']['color'] = 'lightblue'

    fig_rt1.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=X0rt1,
        y0=1,
        x1=X2rt1,
        y1=1,
        opacity=0.6,
        line=dict(
            color="Crimson",
            width=2,
            dash='dash'
    ))

    plot_rt1 = plot(fig_rt1, output_type='div', include_plotlyjs=False, auto_play=False)


    content_trend = {}

    content_trend['plot_rt1'] = plot_rt1
    content_trend['latest_rtdate'] = latest_d_rt1
    content_trend['latest_rt'] = rt1

    return content_trend


# Global keys

state_key = {
    'EC':'Eastern Cape',
    'FS':'Free State',
    'GP':'Gauteng',
    'KZN':'Kwazulu Natal',
    'LP':'Limpopo',
    'MP':'Mpumalanga',
    'NC':'Northern Cape',
    'NW':'North West',
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