import datetime
import glob
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot


def plot1d():
    x_data = np.arange(0, 120, 0.1)
    trace1 = go.Scatter(
        x=x_data,
        y=np.sin(x_data)
    )

    data = [trace1]
    layout = go.Layout(
        # autosize=False,
        # width=900,
        # height=500,

        xaxis=dict(
            autorange=True
        ),
        yaxis=dict(
            autorange=True
        )
    )
    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

def plotStates():
    url = 'https://raw.githubusercontent.com/dsfsi/covid19za/master/data/covid19za_provincial_cumulative_timeline_confirmed.csv'
    states = pd.read_csv(url,
                     parse_dates=['date'], dayfirst=True,
                     squeeze=True)

    state_filter = list(state_key.keys())
    state_filter.insert(0,'date')

    state_plot = states[state_filter]
    state_plot = state_plot.rename(columns={'date':'Date'})
    state_plotly = state_plot.melt(id_vars='Date', var_name='Province', value_name='Cases')

    fig = px.bar(state_plotly, x='Date', y='Cases', color='Province')
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div


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
