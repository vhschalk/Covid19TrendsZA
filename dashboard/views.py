from django.shortcuts import render
from .matplot import get_matplot
import os

import urllib, base64

def home(request):

    analytics_id = os.environ['G_ANALYTICS_ID']

    return render(request, 'home.html', {'analytics_id':analytics_id})


def matplot(request):

    matplot_fig = get_matplot()

    return render(request, 'matplot.html', matplot_fig)
