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

    state_filter = list(state_key.keys())

    state_filter_t = copy.deepcopy(state_filter)
    state_filter_t.insert(0,'Total RSA')

    state_filter_all = copy.deepcopy(state_filter)
    state_filter_all.insert(0,'Total RSA')
    state_filter_all.append('Date')

    # SA Population


    # Download and fill stats

    ## Cases
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv'
    states_cases_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True, index_col=0)

    casezero = states_cases_i.index[0]
    caselast = states_cases_i.index[-1]

    idx = pd.date_range(casezero, caselast)

    states_cases_i = states_cases_i.reindex(idx, method='ffill')
    states_cases_i = states_cases_i.rename(columns={'total':'Total RSA'})

    states_cases = states_cases_i.copy()
    states_cases = states_cases.reset_index()
    states_cases = states_cases.rename(columns={'index':'Date'})

    ## Deaths
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_deaths.csv'
    states_deaths_i = pd.read_csv(url,
                        parse_dates=['date'], dayfirst=True,
                        squeeze=True,index_col=0).sort_index()

    states_deaths_i = states_deaths_i.reindex(idx, method='ffill')

    states_deaths_i.iloc[0, :] = states_deaths_i.iloc[0, :].replace({np.nan:0})
    states_deaths_i = states_deaths_i.ffill(axis=0)
    states_deaths_i = states_deaths_i.rename(columns={'total':'Total RSA'})

    states_deaths = states_deaths_i.copy()
    states_deaths = states_deaths.reset_index()
    states_deaths = states_deaths.rename(columns={'index':'Date'})

    ## Recovery
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_recoveries.csv'
    states_recovery_i = pd.read_csv(url,
                        parse_dates=['date'], dayfirst=True,
                        squeeze=True,index_col=0).sort_index()

    states_recovery_i = states_recovery_i.reindex(idx, method='ffill')

    states_recovery_i.iloc[0, :] = states_recovery_i.iloc[0, :].replace({np.nan:0})
    states_recovery_i = states_recovery_i.ffill(axis=0)
    states_recovery_i = states_recovery_i.rename(columns={'total':'Total RSA'})

    states_recovery = states_recovery_i.copy()
    states_recovery = states_recovery.reset_index()
    states_recovery = states_recovery.rename(columns={'index':'Date'})

    ## Tests
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_timeline_testing.csv'
    states_tests_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, index_col=0)
    states_tests_i = states_tests_i['cumulative_tests']

    states_tests_i = states_tests_i.reindex(idx, method='ffill')

    states_tests_i = states_tests_i.ffill(axis=0)
    states_tests_i = states_tests_i.rename('Total RSA')

    states_tests = states_tests_i.copy()
    states_tests = states_tests.reset_index()
    states_tests = states_tests.rename(columns={'index':'Date'})


    # Analysis per province

    colour_series = px.colors.qualitative.Vivid


    filter_cases = states_cases[state_filter_all]
    analysis_cases = filter_cases.melt(id_vars='Date', var_name='Province', value_name='Value')
    analysis_cases['Data'] = 'Cases'

    filter_recovery = states_recovery[state_filter_all]
    analysis_recovery = filter_recovery.melt(id_vars='Date', var_name='Province', value_name='Value')
    analysis_recovery['Data'] = 'Recovered'

    filter_deaths = states_deaths[state_filter_all]
    analysis_deaths = filter_deaths.melt(id_vars='Date', var_name='Province', value_name='Value')
    analysis_deaths['Data'] = 'Deaths'


    filter_add = pd.concat([filter_deaths, filter_recovery])
    filter_add = filter_add.groupby('Date').sum()

    filter_sub = filter_add.rmul(-1).reset_index()

    filter_active_i = pd.concat([filter_cases, filter_sub])
    filter_active_i = filter_active_i.groupby('Date').sum()
    filter_active = filter_active_i.reset_index()
    filter_active = filter_active.rename(columns={'index':'Date'})

    analysis_active = filter_active.melt(id_vars='Date', var_name='Province', value_name='Value')
    analysis_active['Data'] = 'Active'

    analysis_all = pd.concat([analysis_cases, analysis_active, analysis_recovery, analysis_deaths])

    analysis_states = analysis_all.query(f"Province != 'Total RSA'")
    analysis_country = analysis_all.query(f"Province == 'Total RSA'")


    ## Plot analysis for provinces

    template_h = '%{y}'

    fig_analysis_prov = px.bar(analysis_states, title='Analysis For Provinces',
                x='Date', y='Value', color='Province', animation_frame='Data',
                barmode='relative', color_discrete_sequence=colour_series)

    fig_analysis_prov.update_layout(plot_bgcolor="#FFF",hovermode="x", height=650)
    fig_analysis_prov.update_xaxes(linecolor="#BCCCDC")
    fig_analysis_prov.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    fig_analysis_prov.update_traces(hovertemplate=template_h)
    fig_analysis_prov["layout"].pop("updatemenus") # remove play controls

    plot_analsysis_prov = plot(fig_analysis_prov, output_type='div', include_plotlyjs=False, auto_play=False)


    ## Plot analysis for deaths

    analysis_states_deaths = analysis_deaths.query(f"Province != 'Total RSA'")


    fig_analysis_death = px.bar(analysis_states_deaths, title='Analysis For Deaths',
                x='Date', y='Value', color='Province',
                barmode='relative', color_discrete_sequence=colour_series)

    fig_analysis_death.update_layout(plot_bgcolor="#FFF")
    fig_analysis_death.update_xaxes(linecolor="#BCCCDC")
    fig_analysis_death.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    fig_analysis_death.update_traces(hovertemplate=None)
    fig_analysis_death.update_layout(hovermode="x")

    plot_analsysis_deaths = plot(fig_analysis_death, output_type='div', include_plotlyjs=False)


    ## Plot analysis for South Africa

    states_tests['Province'] = 'Total RSA'
    states_tests['Data'] = 'Tests'
    states_tests = states_tests.rename(columns={'Total RSA':'Value'})

    analysis_country = pd.concat([analysis_country, states_tests])


    px_data_sa = px.line(analysis_country, x='Date', y='Value', color='Data', line_shape='spline')
    fig_analysis_sa = make_subplots(specs=[[{"secondary_y": True}]])


    fig_analysis_sa.add_trace(px_data_sa['data'][0], secondary_y=True)
    fig_analysis_sa.add_trace(px_data_sa['data'][1], secondary_y=True)
    fig_analysis_sa.add_trace(px_data_sa['data'][2], secondary_y=True)
    fig_analysis_sa.add_trace(px_data_sa['data'][3], secondary_y=True)
    fig_analysis_sa.add_trace(px_data_sa['data'][4], secondary_y=False)

    fig_analysis_sa.update_yaxes(title_text="Rest of Data", secondary_y=True)
    fig_analysis_sa.update_yaxes(title_text="Tests", secondary_y=False)
    fig_analysis_sa.update_layout(title="Analysis for South Africa")

    fig_analysis_sa.update_layout(plot_bgcolor="#FFF", hovermode="x")

    fig_analysis_sa.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1, linecolor="#BCCCDC")
    fig_analysis_sa.update_yaxes(showspikes=True, spikethickness=1, linecolor="#BCCCDC", gridcolor='#D3D3D3')
    fig_analysis_sa.update_layout(spikedistance=1000, hoverdistance=100)

    fig_analysis_sa.update_traces(hovertemplate=None)

    plot_analysis_sa = plot(fig_analysis_sa, output_type='div', include_plotlyjs=False)


    ## Summary

    latest_date = caselast.strftime("%d %B %Y")
    f_date = caselast.strftime("%Y-%m-%d")

    analysis_latest = analysis_country.query(f"Date == '{f_date}'")

    latest_cases = format_comma(analysis_latest.iloc[0]['Value'])
    latest_active = format_comma(analysis_latest.iloc[1]['Value'])
    latest_recovery = format_comma(analysis_latest.iloc[2]['Value'])
    latest_deaths = format_comma(analysis_latest.iloc[3]['Value'])
    latest_tests = format_comma(analysis_latest.iloc[4]['Value'])


    ## Plot analysis per province

    max_states = max(analysis_states['Value']) * 1.05


    fig_analaysis_prov2 = px.line(analysis_states, title='Analysis Per Provinces',
                x='Date', y='Value', color='Data', animation_frame='Province',
                line_shape='spline', range_y=[0, max_states],
                color_discrete_sequence=colour_series)

    fig_analaysis_prov2.update_layout(plot_bgcolor="#FFF", height=550)
    fig_analaysis_prov2.update_xaxes(linecolor="#BCCCDC")
    fig_analaysis_prov2.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    fig_analaysis_prov2.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1)
    fig_analaysis_prov2.update_yaxes(showspikes=True, spikethickness=1)
    fig_analaysis_prov2.update_layout(spikedistance=1000, hoverdistance=100)

    fig_analaysis_prov2.update_traces(hovertemplate=template_h)
    fig_analaysis_prov2.update_layout(hovermode="x")
    fig_analaysis_prov2["layout"].pop("updatemenus") # remove play controls

    plot_analsysis_prov2 = plot(fig_analaysis_prov2, output_type='div', include_plotlyjs=False, auto_play=False)


    # Daily analaysis

    def shape_daily(states_df_i, label, fil=True):
        if fil:
            all_df = states_df_i[state_filter_t]
        else:
            all_df = states_df_i
        daily_df_i = all_df.diff()
        daily_df_i = daily_df_i[1:]
        daily_df = daily_df_i.reset_index()
        daily_df = daily_df.rename(columns={'index':'Date'})
        daily_melt_df = daily_df.melt(id_vars='Date', var_name='Province', value_name='Value')
        daily_melt_df['Data'] = label
        return daily_melt_df, daily_df_i

    daily_melt_cases, daily_cases = shape_daily(states_cases_i, 'Cases')
    daily_melt_active, x = shape_daily(filter_active_i, 'Active')
    daily_melt_recovery, x = shape_daily(states_recovery_i, 'Recovery')
    daily_melt_deaths, x = shape_daily(states_deaths_i, 'Deaths')

    states_cases_smoothed = daily_cases.rolling(7,
        win_type='gaussian',
        min_periods=1,
        center=True).mean(std=2).round()

    daily_smoothed = states_cases_smoothed.reset_index()
    daily_smoothed = daily_smoothed.rename(columns={'index':'Date'})
    daily_melt_smoothed = daily_smoothed.melt(id_vars='Date', var_name='Province', value_name='Value')
    daily_melt_smoothed['Data'] = 'Cases Smoothed'

    daily_all = pd.concat([daily_melt_cases, daily_melt_smoothed, daily_melt_active, daily_melt_recovery, daily_melt_deaths])

    daily_country = daily_all.query(f"Province == 'Total RSA'")
    daily_states = daily_all.query(f"Province != 'Total RSA'")

    daily_melt_tests, x = shape_daily(states_tests_i, 'Tests', False)

    daily_country = pd.concat([daily_country, daily_melt_tests])


    ## Plot daily change for South Africa

    px_daily_sa = px.line(daily_country, x='Date', y='Value', color='Data') # temporary remove line_shape='spline'
    fig_daily_sa = make_subplots(rows=1, cols=2)


    #visible="legendonly"
    fig_daily_sa.add_trace(px_daily_sa['data'][0], row=1, col=1)
    fig_daily_sa.add_trace(px_daily_sa['data'][1], row=1, col=1)
    fig_daily_sa.add_trace(px_daily_sa['data'][2], row=1, col=2)
    fig_daily_sa.add_trace(px_daily_sa['data'][3], row=1, col=2)
    fig_daily_sa.add_trace(px_daily_sa['data'][4], row=1, col=2)
    fig_daily_sa.add_trace(px_daily_sa['data'][5], row=1, col=1)

    fig_daily_sa.update_layout(plot_bgcolor="#FFF")
    fig_daily_sa.update_xaxes(linecolor="#BCCCDC")
    fig_daily_sa.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    fig_daily_sa.update_layout(title="Daily Change for South Africa")

    fig_daily_sa.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1)
    fig_daily_sa.update_yaxes(showspikes=True, spikethickness=1, spikemode="across")
    fig_daily_sa.update_layout(spikedistance=1000, hoverdistance=100)

    fig_daily_sa.update_traces(hovertemplate=None)
    fig_daily_sa.update_layout(hovermode="x")

    plot_daily_sa = plot(fig_daily_sa, output_type='div', include_plotlyjs=False)


    # Plot daily change for provinces

    max_daily = max(daily_states['Value']) * 1.05
    min_daily = min(daily_states['Value']) * 1.05


    fig_daily_prov = px.line(daily_states, title='Daily Change For Provinces',
                x='Date', y='Value', color='Data', animation_frame='Province',
                range_y=[min_daily, max_daily], line_shape='spline',
                color_discrete_sequence=colour_series)

    fig_daily_prov.update_layout(plot_bgcolor="#FFF", height=550)
    fig_daily_prov.update_xaxes(linecolor="#BCCCDC")
    fig_daily_prov.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    fig_daily_prov.update_traces(hovertemplate=template_h)
    fig_daily_prov.update_layout(hovermode="x")
    fig_daily_prov["layout"].pop("updatemenus") # remove play controls

    fig_daily_prov.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1)
    fig_daily_prov.update_yaxes(showspikes=True, spikethickness=1)
    fig_daily_prov.update_layout(spikedistance=1000, hoverdistance=100)

    plot_daily_prov = plot(fig_daily_prov, output_type='div', include_plotlyjs=False, auto_play=False)


    # Rt analysis

    # Rt model 2
    
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_mcmc.csv'
    state_rt_mcmc = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True)
    state_rt_mcmc = state_rt_mcmc.rename(columns={'date':'Date'})
    state_rt_mcmc = state_rt_mcmc.rename(columns={'Median':'Rt'})


    # Rt model 2 summary

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
                title='Rt for Covid-19 in South Africa', line_shape='spline')
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

    fig_rt2.update_layout(plot_bgcolor="#FFF")
    fig_rt2.update_xaxes(linecolor="#BCCCDC")
    fig_rt2.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    plot_rt_country = plot(fig_rt2, output_type='div', include_plotlyjs=False)


    ## Complete content dict

    content_trend['plot_rt_country'] = plot_rt_country
    content_trend['latest_rt'] = rt2
    content_trend['latest_rt2date'] = latest_d_rt2
    content_trend['plot_analsysis_prov'] = plot_analsysis_prov
    content_trend['plot_analsysis_deaths'] = plot_analsysis_deaths
    content_trend['plot_analysis_sa'] = plot_analysis_sa
    content_trend['plot_analsysis_prov2'] = plot_analsysis_prov2
    content_trend['plot_daily_sa'] = plot_daily_sa
    content_trend['plot_daily_prov'] = plot_daily_prov
    content_trend['cases'] = latest_cases
    content_trend['recovered'] = latest_recovery
    content_trend['deaths'] = latest_deaths
    content_trend['active'] = latest_active
    content_trend['tests'] = latest_tests
    content_trend['latest_date'] = latest_date

    return content_trend


def future_plots():

    # Setup common variables

    content_future = {}


    # Rt model 2

    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_mcmc.csv'
    state_rt_mcmc = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True)

    latest_rt2 = state_rt_mcmc.iloc[-1]
    rt2 = latest_rt2['Rt']
    rt2h = latest_rt2['High_80']
    rt2l = latest_rt2['Low_80']
    rt2f = round(rt2, 2)
    

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
    if (rt2h not in r_scenarios):
        r_scenarios.append(rt2h)
    if (rt2l not in r_scenarios):
        r_scenarios.append(rt2l)

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

    fig6.update_layout(plot_bgcolor="#FFF")
    fig6.update_xaxes(linecolor="#BCCCDC")
    fig6.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    plot_forecast = plot(fig6, output_type='div', include_plotlyjs=False)

    
    # Graph 2

    increasing_forecast = future_projections.query(f"R > 1")

    fig7 = px.line(increasing_forecast, x='Date', y='Cases',
               animation_frame='R', height=600, range_y=[0, max_country],
               title='Covid-19 Cases Forecast for Increasing Cases (Rt is bigger than 1)')
    fig7.update_layout(hovermode="x")

    fig7.update_layout(plot_bgcolor="#FFF")
    fig7.update_xaxes(linecolor="#BCCCDC")
    fig7.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

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

    fig8.update_layout(plot_bgcolor="#FFF")
    fig8.update_xaxes(linecolor="#BCCCDC")
    fig8.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

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

    fig9.update_layout(plot_bgcolor="#FFF")
    fig9.update_xaxes(linecolor="#BCCCDC")
    fig9.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    plot_scenarios3 = plot(fig9, output_type='div', include_plotlyjs=False, auto_play=False)


    content_future['latest_rt'] = rt2f
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


    # Summary

    rt1_last_df = states_all_rt_i.groupby(level=0)[['ML']].last()
    rt1_states = rt1_last_df['ML'].to_dict()

    state_single = states_all_rt.query("Province == 'Total RSA'")

    state_single["e_plus"] = state_single['High_90'].sub(state_single['Rt'])
    state_single["e_minus"] = state_single['Rt'].sub(state_single['Low_90'])

    X0rt1 = state_single.iloc[0]['Date']
    latest_result_rt = state_single.iloc[-1]
    X2rt1 = latest_result_rt['Date']
    rt1 = latest_result_rt['Rt']

    latest_d_rt1 = X2rt1.strftime("%d %B %Y")


    # Plot Rt country

    fig_rt1 = px.line(state_single, x='Date', y='Rt',
                error_y='e_plus', error_y_minus='e_minus',
                title='Rt for Covid-19 in South Africa (First model)', line_shape='spline')
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

    fig_rt1.update_layout(plot_bgcolor="#FFF")
    fig_rt1.update_xaxes(linecolor="#BCCCDC")
    fig_rt1.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    plot_rt1 = plot(fig_rt1, output_type='div', include_plotlyjs=False, auto_play=False)


    # Plot Rt for Covid-19 in South African provinces

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

    fig_rt_province.update_layout(title_text="Rt for Covid-19 in South African Provinces (First model)", height=700)
    fig_rt_province.update_traces(hovertemplate=None)
    fig_rt_province.update_layout(hovermode="x")

    fig_rt_province.update_layout(plot_bgcolor="#FFF")
    fig_rt_province.update_xaxes(linecolor="#BCCCDC")
    fig_rt_province.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    plot_rt_states = plot(fig_rt_province, output_type='div', include_plotlyjs=False)


    content_trend['plot_rt1'] = plot_rt1
    content_trend['latest_rtdate'] = latest_d_rt1
    content_trend['latest_rt'] = rt1
    content_trend['plot_rt_states'] = plot_rt_states
    content_trend['rt_ec'] = rt1_states['EC']
    content_trend['rt_fs'] = rt1_states['FS']
    content_trend['rt_gp'] = rt1_states['GP']
    content_trend['rt_kzn'] = rt1_states['KZN']
    content_trend['rt_lp'] = rt1_states['LP']
    content_trend['rt_mp'] = rt1_states['MP']
    content_trend['rt_nc'] = rt1_states['NC']
    content_trend['rt_nw'] = rt1_states['NW']
    content_trend['rt_wc'] = rt1_states['WC']

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
