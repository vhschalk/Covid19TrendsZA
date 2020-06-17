from django.shortcuts import render
from .matplot import get_matplot
from .graphly import plots_trends


def home(request):

    plot_rt_country, plot_rt_states, latestrt, latestd, plot_combined_cases, plot_daily_cases, plot_stats, plot_future, summary, future  = plots_trends()

    return render(request, 'home.html', {'G1':plot_rt_country, 'G2':plot_rt_states,'latestrt':latestrt, 'latestd':latestd, 
                  'G3':plot_stats, 'G4':plot_combined_cases, 'G5':plot_daily_cases, 'G6':plot_future, 'summary':summary, 'future':future})


def data(request):

    return render(request)


def export(request):

    return render(request, 'export.html')


def matplot(request):

    matplot_fig = get_matplot()

    return render(request, 'matplot.html', matplot_fig)
