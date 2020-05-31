from django.shortcuts import render
from .matplot import get_matplot
from .graphly import plotStates

def base(request):

    return render(request, 'home.html', {'graphly':''})

def home(request):

    return render(request, 'home.html', {'graphly':''})

def data(request):
    
    graphly = plotStates()

    return render(request, 'data.html', {'graphly':graphly})

def matplot(request):

    matplot_fig = get_matplot()

    return render(request, 'matplot.html', matplot_fig)
