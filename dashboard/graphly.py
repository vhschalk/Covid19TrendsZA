import copy, math
import datetime
import glob
import sys
import os
from datetime import timedelta, date, datetime

from django.core.exceptions import MultipleObjectsReturned

from django_pandas.io import read_frame

from decimal import Decimal
import csv
import requests
import threading
import json

from .models import CovidData, LatestUpdate, ReproductionNum

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot
from plotly.subplots import make_subplots

# Change to avoid temporary delays
repo = 'dsfsi'
repo_rt = 'dsfsi'

# Global variables

date_zero = None
date_last = None

template_h = '%{y}'



def sync_all_data_providers():

    # TODO: should check for empty DB
    #try:
    #    recordC = CovidData.objects.filter(Var = 'C').order_by('date')
    #except LatestUpdate.DoesNotExist:
    #    data_gen_provider('C', 'confirmed')

    print('START Saving')

    data_gen_shape('C', 'confirmed')
    data_gen_shape('R', 'recoveries')
    data_gen_shape('D', 'deaths')
    data_active_shape()
    data_test_shape()

    data_rep1_provider()
    data_rep2_provider()

    print('DONE Saving')


def data_gen_provider(data_var, filepart):

    urlC = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/covid19za_provincial_cumulative_timeline_' + filepart + '.csv'
    with requests.Session() as s:
        download = s.get(urlC)
        decode_content = download.content.decode('utf-8').splitlines()

        covid_reader = csv.reader(decode_content, delimiter=',')

        try:
            updated = LatestUpdate.objects.get(Var = data_var).Date
        except LatestUpdate.DoesNotExist:
            updated = date(2000,1,1)
        except:
            print('No updated record ERROR for ' + data_var + ':', sys.exc_info())
        
        
        try:
            covid_data_list = list(covid_reader)
            last_date = datetime.strptime(covid_data_list[-1][0], '%d-%m-%Y').date()

            ## Already up to date, DB save is not required
            if updated == last_date:
                print('Not Saving ' + data_var)
                return None

            
            covid_reader = csv.reader(decode_content, delimiter=',')
            next(covid_reader, None) #skip the header
            print('Saving: ' + data_var)

            for record in covid_reader:

                record_date = datetime.strptime(record[0], '%d-%m-%Y')

                CovidData.objects.update_or_create(
                    Date = record_date, Var = data_var,
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
                        'Unknown' : parse_int(record[11]),
                        'Total' : parse_int(record[12]),
                        'Source' : record[13]
                    },
                )

            LatestUpdate.objects.update_or_create(
                Var = data_var,
                defaults = {'Date' : last_date}
            )

        except MultipleObjectsReturned:
            print('Saving ERROR for ' + data_var + ' at ' + str(record_date) + ':', sys.exc_info())

        except:
            print('Saving ERROR for ' + data_var + ':', sys.exc_info())


def data_gen_shape(data_var, filepart):

    urlC = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/covid19za_provincial_cumulative_timeline_' + filepart + '.csv'

    states_data_i = pd.read_csv(urlC, parse_dates=['date'], dayfirst=True, index_col=0)

    try:
        updated = LatestUpdate.objects.get(Var = data_var).Date
    except LatestUpdate.DoesNotExist:
        updated = date(2000,1,1)
    except:
        print('No updated record ERROR for ' + data_var + ':', sys.exc_info())
    
    try:
        if data_var == 'C':
            global date_zero 
            date_zero = states_data_i.index[0]
            global date_last 
            date_last = states_data_i.index[-1]

        ## Already up to date, DB save is not required
        if updated == date_last:
            print('Not Saving ' + data_var)
            return None

        # Shape data

        idx = pd.date_range(date_zero, date_last)

        states_data_i = states_data_i.reindex(idx, method='ffill')

        states_data_i.iloc[0, :] = states_data_i.iloc[0, :].replace({np.nan:0})
        states_data_i = states_data_i.ffill(axis=0)

        # TODO: Validate totals
        #states_data_i = states_data_i.rename(columns={'total':'total2'})
        #states_data_i = states_data_i[state_filter]
        #states_data_i['Total'] = states_data_i.sum(axis=1)

        # Store data in DB table
        
        for record_date, record in states_data_i.iterrows():

            CovidData.objects.update_or_create(
                Date = record_date, Var = data_var,
                defaults = {
                    'EC' : parse_int(record['EC']),
                    'FS' : parse_int(record['FS']),
                    'GP' : parse_int(record['GP']),
                    'KZN' : parse_int(record['KZN']),
                    'LP' : parse_int(record['LP']),
                    'MP' : parse_int(record['MP']),
                    'NC' : parse_int(record['NC']),
                    'NW' : parse_int(record['NW']),
                    'WC' : parse_int(record['WC']),
                    'Unknown' : parse_int(record['UNKNOWN']),
                    'Total' : parse_int(record['total']),
                    'Source' : record['source']
                },
            )

        LatestUpdate.objects.update_or_create(
            Var = data_var,
            defaults = {'Date' : date_last}
        )
        print('SAVED ' + data_var)

    except MultipleObjectsReturned:
        print('Saving ERROR for ' + data_var + ' at ' + str(record_date) + ':', sys.exc_info())

    except:
        print('Saving ERROR for ' + data_var + ':', sys.exc_info())


def data_active_shape():

    data_var = 'A'

    try:
        updated = LatestUpdate.objects.get(Var = data_var).Date
    except LatestUpdate.DoesNotExist:
        updated = date(2000,1,1)
    except:
        print('No updated record ERROR for ' + data_var + ':', sys.exc_info())
    
    try:

        ## Already up to date, DB save is not required
        if updated == date_last:
            print('Not Saving ' + data_var)
            return None

        # Get latest data sets
        db_cases = CovidData.objects.filter(Var = 'C').order_by('Date')
        states_cases = read_frame(db_cases)
        filter_cases = states_cases[state_filter_all]

        db_deaths = CovidData.objects.filter(Var = 'D').order_by('Date')
        states_deaths = read_frame(db_deaths)
        filter_deaths = states_deaths[state_filter_all]
        
        db_recovery = CovidData.objects.filter(Var = 'R').order_by('Date')
        states_recovery = read_frame(db_recovery)
        filter_recovery = states_recovery[state_filter_all]

        # Calculate active data

        filter_add = pd.concat([filter_deaths, filter_recovery])
        filter_add = filter_add.groupby('Date').sum()

        filter_sub = filter_add.rmul(-1).reset_index()

        filter_active_i = pd.concat([filter_cases, filter_sub])
        filter_active_i = filter_active_i.groupby('Date').sum()

        # Store data in DB table
        
        for record_date, record in filter_active_i.iterrows():

            CovidData.objects.update_or_create(
                Date = record_date, Var = data_var,
                defaults = {
                    'EC' : parse_int(record['EC']),
                    'FS' : parse_int(record['FS']),
                    'GP' : parse_int(record['GP']),
                    'KZN' : parse_int(record['KZN']),
                    'LP' : parse_int(record['LP']),
                    'MP' : parse_int(record['MP']),
                    'NC' : parse_int(record['NC']),
                    'NW' : parse_int(record['NW']),
                    'WC' : parse_int(record['WC']),
                    'Unknown' : parse_int(record['Unknown']),
                    'Total' : parse_int(record['Total']),
                    'Source' : ''
                },
            )

        LatestUpdate.objects.update_or_create(
            Var = data_var,
            defaults = {'Date' : date_last}
        )
        print('SAVED ' + data_var)

    except MultipleObjectsReturned:
        print('Saving ERROR for ' + data_var + ' at ' + str(record_date) + ':', sys.exc_info())

    except:
        print('Saving ERROR for ' + data_var + ':', sys.exc_info())


def data_test_shape():

    data_var = 'T'
    urlC = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/covid19za_timeline_testing.csv'

    states_data_i = pd.read_csv(urlC, parse_dates=['date'], dayfirst=True, index_col=0)

    try:
        updated = LatestUpdate.objects.get(Var = data_var).Date
    except LatestUpdate.DoesNotExist:
        updated = date(2000,1,1)
    except:
        print('No updated record ERROR for ' + data_var + ':', sys.exc_info())
    
    try:
        ## Already up to date, DB save is not required
        if updated == date_last:
            print('Not Saving ' + data_var)
            return None

        # Shape data

        idx = pd.date_range(date_zero, date_last)

        states_data_i = states_data_i[['cumulative_tests','source']]
        states_data_i = states_data_i.reindex(idx, method='ffill')

        states_data_i.iloc[0, :] = states_data_i.iloc[0, :].replace({np.nan:0})
        states_data_i = states_data_i.ffill(axis=0)

        # Store data in DB table
        
        for record_date, record in states_data_i.iterrows():
            
            source = record['source']
            if type(source) == str:
                l = len(record['source'])
                if (l > 400):
                    source = source[:400]
            else:
                source = ''

            CovidData.objects.update_or_create(
                Date = record_date, Var = data_var,
                defaults = {
                    'Total' : parse_int(record['cumulative_tests']),
                    'Source' : source
                },
            )

        LatestUpdate.objects.update_or_create(
            Var = data_var,
            defaults = {'Date' : date_last}
        )
        print('SAVED ' + data_var)

    except MultipleObjectsReturned:
        print('Saving ERROR for ' + data_var + ' at ' + str(record_date) + ':', sys.exc_info())

    except:
        print('Saving ERROR for ' + data_var + ':', sys.exc_info())


def data_rep1_provider():
    data_var = '1'
    
    urlC = 'https://raw.githubusercontent.com/' + repo_rt + '/covid19za/master/data/calc/calculated_rt_sa_provincial_cumulative.csv'
    with requests.Session() as s:
        download = s.get(urlC)

        decode_content = download.content.decode('utf-8').splitlines()

        covid_reader = csv.reader(decode_content, delimiter=',')
        try:
            updated = LatestUpdate.objects.get(Var = data_var).Date
        except LatestUpdate.DoesNotExist:
            updated = date(2000,1,1)
        except:
            print('No updated record ERROR for ' + data_var + ':', sys.exc_info())
        

        try:
            covid_data_list = list(covid_reader)
            last_date = datetime.strptime(covid_data_list[-1][1], '%Y-%m-%d').date()

            ## Already up to date, DB save is not required
            if updated == last_date:
                print('Not Saving ' + data_var)
                return None

            
            covid_reader = csv.reader(decode_content, delimiter=',')
            next(covid_reader, None) #skip the header
            print('Saving: ' + data_var)
            
            for record in covid_reader:

                state = record[0]
                if state == 'Total RSA':
                    state = 'RSA'
                record_date = datetime.strptime(record[1], '%Y-%m-%d')

                ReproductionNum.objects.update_or_create(
                    Date = record_date, Var = 1, Province = state,
                    defaults = {
                        'Rt' : parse_dec(record[2]),
                        'High' : parse_dec(record[3]),
                        'Low' : parse_dec(record[4])
                    }
                )
        
            LatestUpdate.objects.update_or_create(
                Var = data_var,
                defaults = {'Date' : last_date}
            )

        except MultipleObjectsReturned:
            print('Saving ERROR for ' + data_var + ' ' + state + ' at ' + str(record_date) + ':', sys.exc_info())

        except:
            print('Saving ERROR for ' + data_var + ':', sys.exc_info())


def data_rep2_provider():
    data_var = '2'
    
    urlC = 'https://raw.githubusercontent.com/' + repo_rt + '/covid19za/master/data/calc/calculated_rt_sa_mcmc.csv'
    with requests.Session() as s:
        download = s.get(urlC)

        decode_content = download.content.decode('utf-8').splitlines()

        covid_reader = csv.reader(decode_content, delimiter=',')
        try:
            updated = LatestUpdate.objects.get(Var = data_var).Date
        except LatestUpdate.DoesNotExist:
            updated = date(2000,1,1)
        except:
            print('No updated record ERROR for ' + data_var + ':', sys.exc_info())
        

        try:
            covid_data_list = list(covid_reader)
            last_date = datetime.strptime(covid_data_list[-1][0], '%Y-%m-%d').date()

            ## Already up to date, DB save is not required
            if updated == last_date:
                print('Not Saving ' + data_var)
                return None

            
            covid_reader = csv.reader(decode_content, delimiter=',')
            next(covid_reader, None) #skip the header
            print('Saving: ' + data_var)
            
            for record in covid_reader:

                record_date = datetime.strptime(record[0], '%Y-%m-%d')

                ReproductionNum.objects.update_or_create(
                    Date = record_date, Var = 2, Province = 'RSA',
                    defaults = {
                        'Rt' : parse_dec(record[1]),
                        'High' : parse_dec(record[2]),
                        'Low' : parse_dec(record[3]),
                        'Infect' : parse_dec(record[4]),
                        'Adj' : parse_dec(record[5])
                    }
                )
            
            LatestUpdate.objects.update_or_create(
                Var = data_var,
                defaults = {'Date' : last_date}
            )

        except MultipleObjectsReturned:
            print('Saving ERROR for ' + data_var + ' at ' + str(record_date) + ':', sys.exc_info())

        except:
            print('Saving ERROR for ' + data_var + ':', sys.exc_info())


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


def trend_shape():

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
    content_session = {}


    # Download and fill stats

    ## Cases
    db_cases = CovidData.objects.filter(Var = 'C').order_by('Date')
    states_cases_i = read_frame(db_cases, index_col='Date')
    states_cases = read_frame(db_cases)
    content_session['states_cases_i'] = states_cases_i.to_json(orient='split')
    content_session['states_cases'] = states_cases.to_json(orient='split')
    

    ## Deaths
    db_deaths = CovidData.objects.filter(Var = 'D').order_by('Date')
    states_deaths_i = read_frame(db_deaths, index_col='Date')
    states_deaths = read_frame(db_deaths)
    content_session['states_deaths_i'] = states_deaths_i.to_json(orient='split')
    content_session['states_deaths'] = states_deaths.to_json(orient='split')

    ## Recovery
    db_recovery = CovidData.objects.filter(Var = 'R').order_by('Date')
    states_recovery_i = read_frame(db_recovery, index_col='Date')
    states_recovery = read_frame(db_recovery)
    content_session['states_recovery_i'] = states_recovery_i.to_json(orient='split')
    content_session['states_recovery'] = states_recovery.to_json(orient='split')

    ## Active
    db_active = CovidData.objects.filter(Var = 'A').order_by('Date')
    states_active_i = read_frame(db_active, index_col='Date')
    states_active = read_frame(db_active)
    content_session['states_active_i'] = states_active_i.to_json(orient='split')
    content_session['states_active'] = states_active.to_json(orient='split')

    ## Tests
    db_tests = CovidData.objects.filter(Var = 'T').order_by('Date')
    states_tests_i = read_frame(db_tests, index_col='Date')
    states_tests = read_frame(db_tests)
    content_session['states_tests_i'] = states_tests_i.to_json(orient='split')
    content_session['states_tests'] = states_tests.to_json(orient='split')

    # Summary

    caselast = states_cases_i.index[-1]
    latest_date = caselast.strftime("%d %B %Y")

    latest_cases = format_comma(states_cases_i.iloc[-1]['Total'])
    latest_recovery = format_comma(states_recovery_i.iloc[-1]['Total'])
    latest_active = format_comma(states_active_i.iloc[-1]['Total'])
    latest_deaths = format_comma(states_deaths_i.iloc[-1]['Total'])
    latest_tests = format_comma(states_tests_i.iloc[-1]['Total'])

    content_trend['cases'] = latest_cases
    content_trend['recovered'] = latest_recovery
    content_trend['deaths'] = latest_deaths
    content_trend['active'] = latest_active
    content_trend['tests'] = latest_tests
    content_trend['latest_date'] = latest_date


    # Rt model 2 summary
    
    db_rep2 = ReproductionNum.objects.filter(Var = 2).order_by('Date')
    state_rt_mcmc = read_frame(db_rep2)
    content_session['state_rt_mcmc'] = state_rt_mcmc.to_json(orient='split')

    latest_rt2 = state_rt_mcmc.iloc[-1]
    rt2 = round(latest_rt2['Rt'], 2)
    
    content_trend['latest_rt2'] = rt2

    return content_trend, content_session


def session_df(content_session_tag):
    return pd.read_json(content_session_tag, orient='split')
    #return pd.json_normalize(json.loads(content_session_tag))


def plot_rt_country(content_session):

    content_trend = {}

    # Plot: Model 2: Rt for Covid-19 in South Africa
    
    state_rt_mcmc = session_df(content_session['state_rt_mcmc'])
    state_rt_mcmc["e_plus"] = state_rt_mcmc['High'].sub(state_rt_mcmc['Rt'])
    state_rt_mcmc["e_minus"] = state_rt_mcmc['Rt'].sub(state_rt_mcmc['Low'])

    X0rt2 = state_rt_mcmc.iloc[0,:]['Date']

    latest_rt2 = state_rt_mcmc.iloc[-1]
    X1rt2 = latest_rt2['Date']
    rt2 = round(latest_rt2['Rt'], 2)

    X1rt2 = latest_rt2['Date']
    latest_date_rt2 = X1rt2.strftime("%d %B %Y")

    content_trend['latest_rt2'] = rt2
    content_trend['latest_rt2_date'] = latest_date_rt2

    fig_rt2 = px.line(state_rt_mcmc, x='Date', y='Rt',
                error_y='e_plus', error_y_minus='e_minus',
                title='Rt for Covid-19 in South Africa') #, line_shape='spline'
    fig_rt2.update_traces(hovertemplate=None)
    fig_rt2.update_layout(hovermode="x")
    fig_rt2['data'][0]['error_y']['color'] = 'lightblue'

    fig_rt2.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=X0rt2,
        y0=1,
        x1=X1rt2,
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
    
    content_trend['plot_rt_country'] = plot_rt_country

    print('plot_rt_country')
    
    return content_trend


def plot_analysis_for_prov(content_session):

    content_trend = {}

    # Analysis per province

    colour_series = px.colors.qualitative.Vivid
    global state_filter_all

    states_cases = session_df(content_session['states_cases'])
    filter_cases = states_cases[state_filter_all]
    analysis_cases = filter_cases.melt(id_vars='Date', var_name='Province', value_name='Value')
    analysis_cases['Data'] = 'Cases'

    states_recovery = session_df(content_session['states_recovery'])
    filter_recovery = states_recovery[state_filter_all]
    analysis_recovery = filter_recovery.melt(id_vars='Date', var_name='Province', value_name='Value')
    analysis_recovery['Data'] = 'Recovered'

    states_deaths = session_df(content_session['states_deaths'])
    filter_deaths = states_deaths[state_filter_all]
    analysis_deaths = filter_deaths.melt(id_vars='Date', var_name='Province', value_name='Value')
    analysis_deaths['Data'] = 'Deaths'

    states_active = session_df(content_session['states_active'])
    filter_active = states_active[state_filter_all]
    analysis_active = filter_active.melt(id_vars='Date', var_name='Province', value_name='Value')
    analysis_active['Data'] = 'Active'

    analysis_all = pd.concat([analysis_cases, analysis_recovery, analysis_active, analysis_deaths])

    analysis_states = analysis_all.query(f"Province != 'Total'")
    content_session['analysis_states'] = analysis_states.to_json(orient='split')

    analysis_country = analysis_all.query(f"Province == 'Total'")
    content_session['analysis_country'] = analysis_country.to_json(orient='split')


    ## Plot analysis for provinces

    fig_analysis_prov = px.bar(analysis_states, title='Analysis For Provinces',
                x='Date', y='Value', color='Province', animation_frame='Data',
                barmode='relative', color_discrete_sequence=colour_series)

    fig_analysis_prov.update_layout(plot_bgcolor="#FFF",hovermode="x", height=650)
    fig_analysis_prov.update_xaxes(linecolor="#BCCCDC")
    fig_analysis_prov.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    fig_analysis_prov.update_traces(hovertemplate=template_h)
    fig_analysis_prov["layout"].pop("updatemenus") # remove play controls

    plot_analysis_prov = plot(fig_analysis_prov, output_type='div', include_plotlyjs=False, auto_play=False)

    content_trend['plot_analysis_for_prov'] = plot_analysis_prov


    ## Plot analysis for deaths

    analysis_states_deaths = analysis_deaths.query(f"Province != 'Total'")

    fig_analysis_death = px.bar(analysis_states_deaths, title='Analysis For Deaths',
                x='Date', y='Value', color='Province',
                barmode='relative', color_discrete_sequence=colour_series)

    fig_analysis_death.update_layout(plot_bgcolor="#FFF")
    fig_analysis_death.update_xaxes(linecolor="#BCCCDC")
    fig_analysis_death.update_yaxes(linecolor="#BCCCDC", gridcolor='#D3D3D3')

    fig_analysis_death.update_traces(hovertemplate=None)
    fig_analysis_death.update_layout(hovermode="x")

    plot_analysis_deaths = plot(fig_analysis_death, output_type='div', include_plotlyjs=False)

    content_trend['plot_analysis_deaths'] = plot_analysis_deaths

    print('plot_analysis_for_prov')

    return content_trend, content_session


def plot_analysis_sa(content_session):

    content_trend = {}

    ## Plot analysis for South Africa

    states_tests = session_df(content_session['states_tests'])
    states_tests['Province'] = 'Total'
    states_tests['Data'] = 'Tests'
    states_tests = states_tests.rename(columns={'Total':'Value'})
    states_tests = states_tests[['Date','Province','Value','Data']]

    analysis_country = session_df(content_session['analysis_country'])
    analysis_country_all = pd.concat([analysis_country, states_tests])


    px_data_sa = px.line(analysis_country_all, x='Date', y='Value', color='Data') #, line_shape='spline' -- "hv" | "vh" | "hvh" | "vhv"
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

    content_trend['plot_analysis_sa'] = plot_analysis_sa

    print('plot_analysis_sa')
    
    return content_trend


def plot_analysis_per_prov(content_session):

    content_trend = {}

    ## Plot analysis per province

    analysis_states = session_df(content_session['analysis_states'])
    max_states = np.percentile(analysis_states['Value'], 99)

    colour_series = px.colors.qualitative.Vivid

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

    plot_analysis_prov2 = plot(fig_analaysis_prov2, output_type='div', include_plotlyjs=False, auto_play=False)

    content_trend['plot_analysis_per_prov'] = plot_analysis_prov2

    print('plot_analysis_per_prov')
    
    return content_trend


def plot_daily_sa(content_session):

    content_trend = {}

    # Daily analaysis

    global state_filter

    state_filter_t = copy.deepcopy(state_filter)
    state_filter_t.insert(0,'Total')

    def shape_daily(states_df_i, label, fil=True):
        if fil:
            all_df = states_df_i[state_filter_t]
        else:
            all_df = states_df_i['Total']
        daily_df_i = all_df.diff()
        daily_df_i = daily_df_i[1:]
        daily_df = daily_df_i.reset_index()
        daily_df = daily_df.rename(columns={'index':'Date'})
        daily_melt_df = daily_df.melt(id_vars='Date', var_name='Province', value_name='Value')
        daily_melt_df['Data'] = label
        return daily_melt_df #, daily_df_i

    states_cases_i = session_df(content_session['states_cases_i'])
    states_active_i = session_df(content_session['states_active_i'])
    states_recovery_i = session_df(content_session['states_recovery_i'])
    states_deaths_i = session_df(content_session['states_deaths_i'])
    states_tests_i = session_df(content_session['states_tests_i'])

    daily_melt_cases = shape_daily(states_cases_i, 'Cases') #, daily_cases -> was previously returned in daily_fd_i
    daily_melt_active = shape_daily(states_active_i, 'Active')
    daily_melt_recovery = shape_daily(states_recovery_i, 'Recovery')
    daily_melt_deaths = shape_daily(states_deaths_i, 'Deaths')
    daily_melt_tests = shape_daily(states_tests_i, 'Tests', False)

    daily_all = pd.concat([daily_melt_cases, daily_melt_active, daily_melt_recovery, daily_melt_deaths]) #daily_melt_smoothed

    daily_country = daily_all.query(f"Province == 'Total'")
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

    content_trend['plot_daily_sa'] = plot_daily_sa


    # Plot daily change per provinces

    colour_series = px.colors.qualitative.Vivid

    def daily_change_per_province(daily_melt_data, title, c):
        daily_states = daily_melt_data.query(f"Province != 'Total'")

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

    content_trend['plot_daily_prov_cases'] = plot_daily_prov_cases
    content_trend['plot_daily_prov_recovery'] = plot_daily_prov_recovery
    content_trend['plot_daily_prov_active'] = plot_daily_prov_active
    content_trend['plot_daily_prov_deaths'] = plot_daily_prov_deaths  

    print('plot_daily_sa')  

    return content_trend


def future_plots(content_session):

    # Setup common variables

    content_future = {}

    country_pop = 58775020


    # Downloads Rt model 2 calc data
    state_rt_mcmc = session_df(content_session['state_rt_mcmc'])

    latest_rt2 = state_rt_mcmc.iloc[-1]
    rt2 = float(latest_rt2['Rt'])
    rt2h = float(latest_rt2['High'])
    rt2l = float(latest_rt2['Low'])
    rt2f = round(rt2, 2)


    # Download latest stats

    states_cases_i = session_df(content_session['states_cases_i'])

    states_all = states_cases_i.copy()
    states_all = states_all.reset_index()

    cases_series = pd.Series(states_cases_i['Total'].values, index=states_cases_i.index.values, name='Cases')


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

    print('future_plots')

    return content_future


def format_comma(num):
    return f'{num:,.0f}'


def rt_model1():

    # Setup common variables

    content_trend = {}

    #state_labels = list(state_key.values())


    # Rt mode 1
    db_rep1 = ReproductionNum.objects.filter(Var = 1).order_by('Date')  
    states_all_rt_i = read_frame(db_rep1, index_col='Province')
    
    states_all_rt = states_all_rt_i.copy()
    states_all_rt = states_all_rt.reset_index()


    # Summary
    rt1_last_df = states_all_rt_i.groupby(level=0)[['Rt']].last()
    rt1_states = rt1_last_df['Rt'].to_dict()

    state_single = states_all_rt.query("Province == 'RSA'")

    #state_single["e_plus"] = state_single['High_90'].sub(state_single['Rt'])
    #state_single["e_minus"] = state_single['Rt'].sub(state_single['Low_90'])

    X0rt1 = states_all_rt_i.iloc[0]['Date']

    latest_result_rt = state_single.iloc[-1]
    X2rt1 = latest_result_rt['Date']
    rt1 = latest_result_rt['Rt']

    latest_d_rt1 = X2rt1.strftime("%d %B %Y")


    # Find errors in data
    state_label_err = []
    for key in state_key:
        if key in rt1_states:
            state_label_err.append(state_key.get(key))


    # Plot Rt country

    fig_rt1 = px.line(state_single, x='Date', y='Rt',
                title='Rt for Covid-19 in South Africa (First model version)', line_shape='spline')
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

    states_rt = states_all_rt.query("Province != 'RSA'")

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

    fig_rt_province.update_layout(title_text="Rt for Covid-19 in South African Provinces (First model version)", height=700)
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

state_filter = list(state_key.keys())

state_filter_all = copy.deepcopy(state_filter)
state_filter_all.insert(0,'Total')
state_filter_all.append('Unknown')
state_filter_all.append('Date')
