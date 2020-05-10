from django.shortcuts import render

import urllib, base64
import io

from matplotlib import pyplot as plt
from matplotlib.dates import date2num, num2date
from matplotlib import dates as mdates
from matplotlib import ticker
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from scipy.interpolate import interp1d

import pandas as pd
import numpy as np

repo = 'dsfsi'

def home(request):

    # Get sa province rt data
    url = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/calc/calculated_rt_sa_provincial_cumulative.csv'
    states_raw = pd.read_csv(url,
                         parse_dates=['date'], dayfirst=True,
                         squeeze=True, index_col=[0,1])


    # Plot SA
    country = states_raw.filter(like='Total RSA', axis=0)

    fig_country, ax = plt.subplots(figsize=(600/72,400/72))
    ax = plot_rt(country, ax, '')
    ax.set_title(f'COVID-19 Confirmed Cases: Real-time $R_t$ for South Africa', size=14)
    fig_country.text(0, 0, 'covid19trends.co.za - Data: DSFSI', size=12, weight='demibold')
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    uri_country = format_fig(fig_country)


    # Plot provinces
    fig_states = state_plot(states_raw, 'South African Provinces', plotscale = 0.92)
    uri_states = format_fig(fig_states)


    # Plot districts
    uri_districts1 = plot_districts('gp', 0.78)
    uri_districts2 = plot_districts('wc', 0.90)

    return render(request, 'home.html', {'country':uri_country,'states':uri_states, 'districts1':uri_districts1, 'districts2':uri_districts2, 'debug':''})


def plot_districts(state, plotscale):
    # Get sa province rt data
    url = 'https://raw.githubusercontent.com/' + repo + '/covid19za/master/data/calc/calculated_rt_' + state + '_district_cumulative.csv'
    districts_raw = pd.read_csv(url,
                         parse_dates=['date'], dayfirst=True,
                         squeeze=True, index_col=[0,1])
    # Plot provinces
    fig_districts = state_plot(districts_raw, state.upper() + ' districts', plotscale)
    return format_fig(fig_districts)


def format_fig(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri


def plot_rt(result, ax, state_name):
    ax.set_title(f"{state_name}")

    # Colors
    ABOVE = [1,0,0]
    MIDDLE = [1,1,1]
    BELOW = [0,0,0]
    cmap = ListedColormap(np.r_[
        np.linspace(BELOW,MIDDLE,25),
        np.linspace(MIDDLE,ABOVE,25)
    ])
    color_mapped = lambda y: np.clip(y, .5, 1.5)-.5

    index = result['ML'].index.get_level_values('date')
    values = result['ML'].values

    # Plot dots and line
    ax.plot(index, values, c='k', zorder=1, alpha=.25)
    ax.scatter(index,
               values,
               s=40,
               lw=.5,
               c=cmap(color_mapped(values)),
               edgecolors='k', zorder=2)

    # Aesthetically, extrapolate credible interval by 1 day either side
    lowfn = interp1d(date2num(index),
                     result['Low_90'].values,
                     bounds_error=False,
                     fill_value='extrapolate')

    highfn = interp1d(date2num(index),
                      result['High_90'].values,
                      bounds_error=False,
                      fill_value='extrapolate')

    extended = pd.date_range(start=pd.Timestamp('2020-03-01'),
                             end=index[-1]+pd.Timedelta(days=1))

    ax.fill_between(extended,
                    lowfn(date2num(extended)),
                    highfn(date2num(extended)),
                    color='k',
                    alpha=.1,
                    lw=0,
                    zorder=3)

    ax.axhline(1.0, c='k', lw=1, label='$R_t=1.0$', alpha=.25);

    # Formatting
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_minor_locator(mdates.DayLocator())

    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.1f}"))
    ax.yaxis.tick_right()
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.margins(0)
    ax.grid(which='major', axis='y', c='k', alpha=.1, zorder=-2)
    ax.margins(0)
    ax.set_ylim(0.0, 5.0)
    ax.set_xlim(pd.Timestamp('2020-03-06'), result.index.get_level_values('date')[-1]+pd.Timedelta(days=1))

    #fig.set_facecolor('w')
    return ax


def state_plot(final_results, title, plotscale):
    state_groups = final_results.groupby('state')

    ncols = 3
    nrows = int(np.ceil(len(state_groups) / ncols))

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, nrows*3))

    for i, (state_name, result) in enumerate(state_groups):
        axes.flat[i] = plot_rt(result, axes.flat[i], state_name)

    fig.tight_layout()
    fig.set_facecolor('w')

    fig.suptitle(f'COVID-19 Confirmed Cases: Real-time $R_t$ for ' + title, size=20)
    fig.text(0, 0, 'covid19trends.co.za - Data: DSFSI', size=16, weight='demibold')
    fig.subplots_adjust(top = plotscale)

    return fig
