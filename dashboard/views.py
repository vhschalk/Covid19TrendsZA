from django.shortcuts import render
from .matplot import get_matplot
from .graphly import trend_plots, plot_rt_country, plot_analysis_for_prov, plot_analysis_sa, plot_analysis_per_prov, plot_daily_sa, future_plots, rt_model1


def home(request):

    return render(request, 'home.html')

def home_stats(request):

    content = trend_plots()

    return render(request, 'home_stats.html', {'content':content})

def home_rt_country(request):

    content = plot_rt_country()

    return render(request, 'home_rt_country.html', {'content':content})

def home_analysis_for_prov(request):

    content = plot_analysis_for_prov()

    return render(request, 'home_analysis_for_prov.html', {'content':content})

def home_analysis_sa(request):

    content = plot_analysis_sa()

    return render(request, 'home_analysis_sa.html', {'content':content})

def home_analysis_per_prov(request):

    content = plot_analysis_per_prov()

    return render(request, 'home_analysis_per_prov.html', {'content':content})

def home_daily_sa(request):

    content = plot_daily_sa()

    return render(request, 'home_daily_sa.html', {'content':content})


def home_forecast(request):

    content = future_plots()

    return render(request, 'home_forecast.html', {'content':content})






def export(request):

    return render(request, 'export.html')


def matplot(request):

    matplot_fig = get_matplot()

    return render(request, 'matplot.html', matplot_fig)


def rtmodel1(request):

    content = rt_model1()

    return render(request, 'rtmodel1.html', {'content':content})


def snapshot(request):

    content_trend  = trend_plots()
    content_future = future_plots()

    return render(request, 'snapshot.html', {'content_trend':content_trend, 'content_future':content_future})
