from django.shortcuts import render
#import matplot
import os

import urllib, base64

def home(request):

    analytics_id = os.environ['G_ANALYTICS_ID']

    return render(request, 'home.html', {'analytics_id':analytics_id})


def matplot(request):

    return render(request, 'matplot.html', get_matplot())
