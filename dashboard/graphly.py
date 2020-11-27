import copy, math
import datetime
import glob
import sys
import os
from datetime import timedelta, date, datetime

from django_pandas.io import read_frame

from decimal import Decimal
import csv
import requests
import threading

from .models import CovidData, LatestUpdate, ReproductionNum

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot
from plotly.subplots import make_subplots

# Change to avoid temporary delays
repo = 'dsfsi' #dsfsi



### TODO move to own class

def sync_all_data_providers():

    # TODO: should check for empty DB
    #try:
    #    recordC = CovidData.objects.filter(var = 'C').order_by('date')
    #except LatestUpdate.DoesNotExist:
    #    data_gen_provider('C', 'confirmed')


    print('START RECORDING')
    data_gen_provider('C', 'confirmed')
    #data_gen_provider('A', '')
    data_gen_provider('R', 'recoveries')
    data_gen_provider('D', 'deaths')
    data_test_provider()

    data_rep1_provider()
    data_rep2_provider()
    print('DONE RECORDING')


def data_gen_provider(data_var, filepart):

    urlC = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_' + filepart + '.csv'
    with requests.Session() as s:
        download = s.get(urlC)
        decode_content = download.content.decode('utf-8').splitlines()

        covid_reader = csv.reader(decode_content, delimiter=',')
        try:
            updated = LatestUpdate.objects.get(var = data_var).date
        except LatestUpdate.DoesNotExist:
            updated = date(2000,1,1)
        except:
            print('No updated record ERROR for ' + data_var + ':', sys.exc_info()[0])
        
        
        try:
            covid_data_list = list(covid_reader)
            last_date = datetime.strptime(covid_data_list[-1][0], '%d-%m-%Y').date()

            ## Already up to date, DB save is not required
            if updated == last_date:
                print('Not saving ' + data_var)
                return None

            
            covid_reader = csv.reader(decode_content, delimiter=',')
            next(covid_reader, None) #skip the header
            print('Recording: ' + data_var)

            for record in covid_reader:

                record_date = datetime.strptime(record[0], '%d-%m-%Y')

                CovidData.objects.update_or_create(
                    date = record_date, var = data_var,
                    defaults = {
                        'EC' : parse_int(record[2]),
                        'FS' : parse_int(record[3]),
                        'GP' : parse_int(record[4]),
                        'KZN' : parse_int(record[5]),
                        'LP' : parse_int(record[6]),
                        'MP' : parse_int(record[7]),
                        'NC' : parse_int(record[8]),
                        'NW' : parse_int(record[9]),
                        'WC' : parse_int(record[10]),
                        'unknown' : parse_int(record[11]),
                        'total' : parse_int(record[12]),
                        'source' : record[13]
                    },
                )

            LatestUpdate.objects.update_or_create(
                var = data_var,
                defaults = {'date' : last_date}
            )

        except:
            print('Recording ERROR for ' + data_var + ':', sys.exc_info()[0])


def data_test_provider():
    data_var = 'T'

    urlC = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_timeline_testing.csv'
    with requests.Session() as s:
        download = s.get(urlC)

        decode_content = download.content.decode('utf-8').splitlines()

        covid_reader = csv.reader(decode_content, delimiter=',')
        try:
            updated = LatestUpdate.objects.get(var = data_var).date
        except LatestUpdate.DoesNotExist:
            updated = date(2000,1,1)
        except:
            print('No updated record ERROR for ' + data_var + ':', sys.exc_info()[0])
        

        try:
            covid_data_list = list(covid_reader)
            last_date = datetime.strptime(covid_data_list[-1][0], '%d-%m-%Y').date()

            ## Already up to date, DB save is not required
            if updated == last_date:
                print('Not saving ' + data_var)
                return None

            
            covid_reader = csv.reader(decode_content, delimiter=',')
            next(covid_reader, None) #skip the header
            print('Recording: ' + data_var)

            for record in covid_reader:

                record_date = datetime.strptime(record[0], '%d-%m-%Y')

                CovidData.objects.update_or_create(
                    date = record_date, var = data_var,
                    defaults = {
                        'total' : parse_int(record[2]),
                        'source' : record[13]
                    }
                )
            
            LatestUpdate.objects.update_or_create(
                var = data_var,
                defaults = {'date' : last_date}
            )

        except:
            print('Recording ERROR for ' + data_var + ':', sys.exc_info()[0])


def data_rep1_provider():
    data_var = '1'
    
    urlC = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_provincial_cumulative.csv'
    with requests.Session() as s:
        download = s.get(urlC)

        decode_content = download.content.decode('utf-8').splitlines()

        covid_reader = csv.reader(decode_content, delimiter=',')
        try:
            updated = LatestUpdate.objects.get(var = data_var).date
        except LatestUpdate.DoesNotExist:
            updated = date(2000,1,1)
        except:
            print('No updated record ERROR for ' + data_var + ':', sys.exc_info()[0])
        

        try:
            covid_data_list = list(covid_reader)
            last_date = datetime.strptime(covid_data_list[-1][1], '%Y-%m-%d').date()

            ## Already up to date, DB save is not required
            if updated == last_date:
                print('Not saving ' + data_var)
                return None

            
            covid_reader = csv.reader(decode_content, delimiter=',')
            next(covid_reader, None) #skip the header
            print('Recording: ' + data_var)
            
            for record in covid_reader:

                state = record[0]
                if state == 'Total RSA':
                    state = 'RSA'
                record_date = datetime.strptime(record[1], '%Y-%m-%d')

                ReproductionNum.objects.update_or_create(
                    date = record_date, var = 1,
                    defaults = {
                        'rt' : parse_dec(record[2]),
                        'high' : parse_dec(record[3]),
                        'low' : parse_dec(record[4])
                    }
                )
        
            LatestUpdate.objects.update_or_create(
                var = data_var,
                defaults = {'date' : last_date}
            )

        except:
            print('Recording ERROR for ' + data_var + ':', sys.exc_info()[0])


def data_rep2_provider():
    data_var = '2'
    
    urlC = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_mcmc.csv'
    with requests.Session() as s:
        download = s.get(urlC)

        decode_content = download.content.decode('utf-8').splitlines()

        covid_reader = csv.reader(decode_content, delimiter=',')
        try:
            updated = LatestUpdate.objects.get(var = data_var).date
        except LatestUpdate.DoesNotExist:
            updated = date(2000,1,1)
        except:
            print('No updated record ERROR for ' + data_var + ':', sys.exc_info()[0])
        

        try:
            covid_data_list = list(covid_reader)
            last_date = datetime.strptime(covid_data_list[-1][0], '%Y-%m-%d').date()

            ## Already up to date, DB save is not required
            if updated == last_date:
                print('Not saving ' + data_var)
                return None

            
            covid_reader = csv.reader(decode_content, delimiter=',')
            next(covid_reader, None) #skip the header
            print('Recording: ' + data_var)
            
            for record in covid_reader:

                record_date = datetime.strptime(record[0], '%Y-%m-%d')

                ReproductionNum.objects.update_or_create(
                    date = record_date, var = 2,
                    defaults = {
                        'rt' : parse_dec(record[1]),
                        'high' : parse_dec(record[2]),
                        'low' : parse_dec(record[3]),
                        'infect' : parse_dec(record[4]),
                        'adj' : parse_dec(record[5])
                    }
                )
            
            LatestUpdate.objects.update_or_create(
                var = data_var,
                defaults = {'date' : last_date}
            )

        except:
            print('Recording ERROR for ' + data_var + ':', sys.exc_info()[0])


def parse_int(str):
    if str == '':
        return 0
    else:
        try:
            return int(str)
        except:
            return 0

def parse_dec(str):
    if str == '':
        return 0
    else: 
        try:
            return Decimal(str)
        except:
            return 0



## Graphly


def trend_plots():

    # Load Data Providers
    thread = threading.Thread(target=sync_all_data_providers, args=())
    thread.daemon = True  
    thread.start()
    
    print('Graphing')


    # Setup common variables

    content_trend = {}

    state_filter = list(state_key.keys())

    state_filter_t = copy.deepcopy(state_filter)
    state_filter_t.insert(0,'total')

    state_filter_all = copy.deepcopy(state_filter)
    state_filter_all.insert(0,'total')
    state_filter_all.append('Date')

    # SA Population


    # Download and fill stats

    ## Cases
    db_cases = CovidData.objects.filter(var = 'C').order_by('date')
    states_cases_i = read_frame(db_cases, index_col='date')

    casezero = states_cases_i.index[0]
    caselast = states_cases_i.index[-1]

    idx = pd.date_range(casezero, caselast)

    states_cases_i = states_cases_i.reindex(idx, method='ffill')
    states_cases_i = states_cases_i.rename(columns={'total':'total2'})
    # Validate totals
    states_cases_i = states_cases_i[state_filter]
    states_cases_i['total'] = states_cases_i.sum(axis=1)

    states_cases = states_cases_i.copy()
    states_cases = states_cases.reset_index()
    states_cases = states_cases.rename(columns={'index':'Date'})

    ## Deaths
    db_deaths = CovidData.objects.filter(var = 'D').order_by('date')
    states_deaths_i = read_frame(db_deaths, index_col='date')

    states_deaths_i = states_deaths_i.reindex(idx, method='ffill')

    states_deaths_i.iloc[0, :] = states_deaths_i.iloc[0, :].replace({np.nan:0})
    states_deaths_i = states_deaths_i.ffill(axis=0)
    states_deaths_i = states_deaths_i.rename(columns={'total':'total2'})
    # Validate totals
    states_deaths_i = states_deaths_i[state_filter]
    states_deaths_i['total'] = states_deaths_i.sum(axis=1)

    states_deaths = states_deaths_i.copy()
    states_deaths = states_deaths.reset_index()
    states_deaths = states_deaths.rename(columns={'index':'Date'})

    ## Recovery
    db_recovery = CovidData.objects.filter(var = 'R').order_by('date')
    states_recovery_i = read_frame(db_recovery, index_col='date')

    states_recovery_i = states_recovery_i.reindex(idx, method='ffill')

    states_recovery_i.iloc[0, :] = states_recovery_i.iloc[0, :].replace({np.nan:0})
    states_recovery_i = states_recovery_i.ffill(axis=0)
    states_recovery_i = states_recovery_i.rename(columns={'total':'total2'})
    # Validate totals
    states_recovery_i = states_recovery_i[state_filter]
    states_recovery_i['total'] = states_recovery_i.sum(axis=1)

    states_recovery = states_recovery_i.copy()
    states_recovery = states_recovery.reset_index()
    states_recovery = states_recovery.rename(columns={'index':'Date'})

    ## Tests
    db_tests = CovidData.objects.filter(var = 'T').order_by('date')
    states_tests_i = read_frame(db_tests, index_col='date')

    states_tests_i = states_tests_i.reindex(idx) #TODO temp remove -> , method='ffill'

    states_tests_i = states_tests_i.ffill(axis=0)

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

    analysis_all = pd.concat([analysis_cases, analysis_recovery, analysis_active, analysis_deaths])

    analysis_states = analysis_all.query(f"Province != 'total'")
    analysis_country = analysis_all.query(f"Province == 'total'")


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

    analysis_states_deaths = analysis_deaths.query(f"Province != 'total'")


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

    states_tests['Province'] = 'total'
    states_tests['Data'] = 'Tests'
    states_tests = states_tests.rename(columns={'total':'Value'})

    analysis_country = pd.concat([analysis_country, states_tests])


    px_data_sa = px.line(analysis_country, x='Date', y='Value', color='Data') #, line_shape='spline' -- "hv" | "vh" | "hvh" | "vhv"
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
    latest_recovery = format_comma(analysis_latest.iloc[1]['Value'])
    latest_active = format_comma(analysis_latest.iloc[2]['Value'])
    latest_deaths = format_comma(analysis_latest.iloc[3]['Value'])
    latest_tests = format_comma(analysis_latest.iloc[4]['Value'])


    ## Plot analysis per province

    max_states = np.percentile(analysis_states['Value'], 99)


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
            all_df = states_df_i['total']
        daily_df_i = all_df.diff()
        daily_df_i = daily_df_i[1:]
        daily_df = daily_df_i.reset_index()
        daily_df = daily_df.rename(columns={'index':'Date'})
        daily_melt_df = daily_df.melt(id_vars='Date', var_name='Province', value_name='Value')
        daily_melt_df['Data'] = label
        return daily_melt_df #, daily_df_i

    daily_melt_cases = shape_daily(states_cases_i, 'Cases') #, daily_cases -> was previously returned in daily_fd_i
    daily_melt_active = shape_daily(filter_active_i, 'Active')
    daily_melt_recovery = shape_daily(states_recovery_i, 'Recovery')
    daily_melt_deaths = shape_daily(states_deaths_i, 'Deaths')
    daily_melt_tests = shape_daily(states_tests_i, 'Tests', False)

    # Note: Makes the plot more cluttered
    #states_cases_smoothed = daily_cases.rolling(7,
    #    win_type='gaussian',
    #    min_periods=1,
    #    center=True).mean(std=2).round()
    #daily_smoothed = states_cases_smoothed.reset_index()
    #daily_smoothed = daily_smoothed.rename(columns={'index':'Date'})
    #daily_melt_smoothed = daily_smoothed.melt(id_vars='Date', var_name='Province', value_name='Value')
    #daily_melt_smoothed['Data'] = 'Cases Smoothed'

    daily_all = pd.concat([daily_melt_cases, daily_melt_active, daily_melt_recovery, daily_melt_deaths]) #daily_melt_smoothed

    daily_country = daily_all.query(f"Province == 'total'")
    daily_country = pd.concat([daily_country, daily_melt_tests])


    ## Plot daily change for South Africa

    px_daily_sa = px.line(daily_country, x='Date', y='Value', color='Data') # temporary remove line_shape='spline'
    fig_daily_sa = make_subplots(rows=1, cols=2)


    #visible="legendonly"
    fig_daily_sa.add_trace(px_daily_sa['data'][0], row=1, col=1)
    fig_daily_sa.add_trace(px_daily_sa['data'][1], row=1, col=2)
    fig_daily_sa.add_trace(px_daily_sa['data'][2], row=1, col=2)
    fig_daily_sa.add_trace(px_daily_sa['data'][3], row=1, col=2)
    fig_daily_sa.add_trace(px_daily_sa['data'][4], row=1, col=1)

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


    # Plot daily change per provinces

    # Note: Made into separate plot, multiple variables is to cluttere, color='Data'
    #daily_states = daily_all.query(f"Province != 'total'")

    def daily_change_per_province(daily_melt_data, title, c):
        daily_states = daily_melt_data.query(f"Province != 'total'")

        max_daily = np.percentile(daily_states['Value'], 99)
        min_daily = min(daily_states['Value'])
        fig_daily_prov = px.line(daily_states, title='Daily Change For ' + title + ' Per Provinces',
                    x='Date', y='Value', animation_frame='Province',
                    range_y=[min_daily, max_daily],
                    line_shape='spline', color_discrete_sequence=[colour_series[c]])

        fig_daily_prov.update_layout(plot_bgcolor="#FFF", height=550)
        fig_daily_prov.update_xaxes(linecolor="#BCCCDC")
        fig_daily_prov.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

        fig_daily_prov.update_traces(hovertemplate=template_h)
        fig_daily_prov.update_layout(hovermode="x")
        fig_daily_prov["layout"].pop("updatemenus") # remove play controls

        fig_daily_prov.update_xaxes(showspikes=True, spikesnap="cursor", spikemode="across", spikethickness=1)
        fig_daily_prov.update_yaxes(showspikes=True, spikethickness=1)
        fig_daily_prov.update_layout(spikedistance=1000, hoverdistance=100)

        return plot(fig_daily_prov, output_type='div', include_plotlyjs=False, auto_play=False)

    plot_daily_prov_cases = daily_change_per_province(daily_melt_cases, 'Cases', 0)
    plot_daily_prov_recovery = daily_change_per_province(daily_melt_recovery, 'Recovered', 1)
    plot_daily_prov_active = daily_change_per_province(daily_melt_active, 'Active', 2)
    plot_daily_prov_deaths = daily_change_per_province(daily_melt_deaths, 'Deaths', 3)


    # Rt analysis

    # Rt model 2
    
    #url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_mcmc.csv'
    #state_rt_mcmc = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True)
    db_rep2 = ReproductionNum.objects.filter(var = 2).order_by('date')
    state_rt_mcmc = read_frame(db_rep2)

    state_rt_mcmc = state_rt_mcmc.rename(columns={'date':'Date'})
    state_rt_mcmc = state_rt_mcmc.rename(columns={'rt':'Rt'})


    # Rt model 2 summary

    X0rt2 = state_rt_mcmc.iloc[0,:]['Date']

    latest_rt2 = state_rt_mcmc.iloc[-1]
    rt2 = round(latest_rt2['Rt'], 2)

    X2rt2 = latest_rt2['Date']
    latest_d_rt2 = X2rt2.strftime("%d %B %Y")


    # Plot: Model 1: Rt for Covid-19 in South Africa

    state_rt_mcmc["e_plus"] = state_rt_mcmc['high'].sub(state_rt_mcmc['Rt'])
    state_rt_mcmc["e_minus"] = state_rt_mcmc['Rt'].sub(state_rt_mcmc['low'])

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
    #content_trend['plot_daily_prov'] = plot_daily_prov
    content_trend['plot_daily_prov_cases'] = plot_daily_prov_cases
    content_trend['plot_daily_prov_recovery'] = plot_daily_prov_recovery
    content_trend['plot_daily_prov_active'] = plot_daily_prov_active
    content_trend['plot_daily_prov_deaths'] = plot_daily_prov_deaths
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

    country_pop = 58775020


    # Downloads Rt model 2 calc data

    #url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_mcmc.csv'
    #state_rt_mcmc = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True)
    db_rep2 = ReproductionNum.objects.filter(var = 2).order_by('date')
    state_rt_mcmc = read_frame(db_rep2)

    latest_rt2 = state_rt_mcmc.iloc[-1]
    rt2 = float(latest_rt2['rt'])
    rt2h = float(latest_rt2['high'])
    rt2l = float(latest_rt2['low'])
    rt2f = round(rt2, 2)


    # Download latest stats

    #url = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv'
    #states_all_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True, index_col=0)
    db_cases = CovidData.objects.filter(var = 'C').order_by('date')
    states_all_i = read_frame(db_cases, index_col='date')

    states_all = states_all_i.copy()
    states_all = states_all.reset_index()
    states_all = states_all.rename(columns={'date':'Date'})

    cases_series = pd.Series(states_all_i['total'].values, index=states_all_i.index.values, name='Cases')


    # Forecast Calc

    cases_df = cases_series.to_frame()
    cases_df = cases_df.reset_index()
    cases_df = cases_df.rename(columns={'index':'Date'})
    cases_df

    diff = cases_df['Cases'].diff()

    f = 60
    f2 = 30

    r_scenarios = [1.5, 1.4, 1.3, 1.25, 1.2, 1.15, 1.1, 1.075, 1.05, 1.025, 1.0, 0.975, 0.95, 0.925, 0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.25, 0.1]
    if (rt2 not in r_scenarios):
        r_scenarios.append(rt2)
    if (rt2h not in r_scenarios):
        r_scenarios.append(rt2h)
    if (rt2l not in r_scenarios):
        r_scenarios.append(rt2l)
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

    #state_labels = list(state_key.values())


    # Rt mode 1
    #url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/calc/calculated_rt_sa_provincial_cumulative.csv'
    #states_all_rt_i = pd.read_csv(url, parse_dates=['date'], dayfirst=True, squeeze=True, index_col=[0,1])
    db_rep1 = ReproductionNum.objects.filter(var = 2, index_col=['date','state']).order_by('date')
    states_all_rt_i = read_frame(db_rep1)

    states_all_rt = states_all_rt_i.copy()
    states_all_rt = states_all_rt.reset_index()
    states_all_rt = states_all_rt.rename(columns={'date':'Date'})
    states_all_rt = states_all_rt.rename(columns={'rt':'Rt'})
    states_all_rt = states_all_rt.rename(columns={'state':'Province'})


    # Summary

    rt1_last_df = states_all_rt_i.groupby(level=0)[['rt']].last()
    rt1_states = rt1_last_df['rt'].to_dict()

    state_single = states_all_rt.query("Province == 'total'")

    #state_single["e_plus"] = state_single['High_90'].sub(state_single['Rt'])
    #state_single["e_minus"] = state_single['Rt'].sub(state_single['Low_90'])

    X0rt1 = state_single.iloc[0]['Date']
    latest_result_rt = state_single.iloc[-1]
    X2rt1 = latest_result_rt['Date']
    rt1 = latest_result_rt['Rt']

    latest_d_rt1 = X2rt1.strftime("%d %B %Y")


    # Find errors in data

    ss = 0
    pp = 0
    state_label_err = []

    for key in state_key:
        if key in rt1_states:
            state_label_err.append(state_key.get(key))


    # Plot Rt country

    fig_rt1 = px.line(state_single, x='Date', y='Rt',
                title='Rt for Covid-19 in South Africa (First model)', line_shape='spline')
                #error_y='e_plus', error_y_minus='e_minus',
    fig_rt1.update_traces(hovertemplate=None)
    fig_rt1.update_layout(hovermode="x")
    #fig_rt1['data'][0]['error_y']['color'] = 'lightblue'

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

    states_rt = states_all_rt.query("Province != 'total'")

    fig_px = px.line(states_rt, x='Date', y='Rt', color='Province')
    fig_len = len(fig_px['data'])

    fig_rt_province = make_subplots(rows=3, cols=3,
                    subplot_titles=state_label_err,
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


    # Format content 2

    content_trend['plot_rt1'] = plot_rt1
    content_trend['latest_rtdate'] = latest_d_rt1
    content_trend['latest_rt'] = rt1
    content_trend['plot_rt_states'] = plot_rt_states

    content_trend['rt_ec'] = rt1_states.get('EC')
    content_trend['rt_fs'] = rt1_states.get('FS')
    content_trend['rt_gp'] = rt1_states.get('GP')
    content_trend['rt_kzn'] = rt1_states.get('KZN')
    content_trend['rt_lp'] = rt1_states.get('LP')
    content_trend['rt_mp'] = rt1_states.get('MP')
    content_trend['rt_nc'] = rt1_states.get('NC')
    content_trend['rt_nw'] = rt1_states.get('NW')
    content_trend['rt_wc'] = rt1_states.get('WC')

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
