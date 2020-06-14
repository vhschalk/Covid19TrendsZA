from django.shortcuts import render
from .matplot import get_matplot
from .graphly import plots_data, plots_rt


def home(request):

    plot_rt_country, plot_rt_states, latestrt, latestd  = plots_rt()

    return render(request, 'home.html', {'G1':plot_rt_country, 'G2':plot_rt_states,'latestrt':latestrt, 'latestd':latestd})


def data(request):

    plot_combined_cases, plot_daily_cases, plot_stats  = plots_data()

    return render(request, 'data.html', {'G1':plot_stats, 'G2':plot_combined_cases, 'G3':plot_daily_cases})


def export(request):

    return render(request, 'export.html')


def matplot(request):

    matplot_fig = get_matplot()

    return render(request, 'matplot.html', matplot_fig)
