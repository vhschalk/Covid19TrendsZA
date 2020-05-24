from django.shortcuts import render
from .matplot import get_matplot
from .graphly import plot1d
import os

import urllib, base64

def home(request):

    analytics_id = os.environ['G_ANALYTICS_ID']
    graphly = plot1d()

    return render(request, 'home.html', {'graphly':graphly})

def matplot(request):

    matplot_fig = get_matplot()

    return render(request, 'matplot.html', matplot_fig)
