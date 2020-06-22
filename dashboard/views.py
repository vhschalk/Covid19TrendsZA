from django.shortcuts import render
from .matplot import get_matplot
from .graphly import trend_plots, future_plots 


def home(request):

    plot_rt_country, plot_rt_states, latestrt, latestd, plot_combined_cases, plot_daily_cases, plot_stats, summary  = trend_plots()

    return render(request, 'home.html', {'G1':plot_rt_country, 'G2':plot_rt_states,'latestrt':latestrt, 'latestd':latestd, 
                  'G3':plot_stats, 'G4':plot_combined_cases, 'G5':plot_daily_cases, 'summary':summary})

def export(request):

    return render(request, 'export.html')


def forecast(request):

    latestrt, future, future_perc, plot_forecast, plot_scenarios1, plot_scenarios2, plot_scenarios3 = future_plots()

    return render(request, 'forecast.html', {'latestrt':latestrt, 'future':future, 'future_perc':future_perc, 
                  'G1':plot_forecast, 'G2':plot_scenarios1, 'G3':plot_scenarios2, 'G4':plot_scenarios3})


def matplot(request):

    matplot_fig = get_matplot()

    return render(request, 'matplot.html', matplot_fig)
