from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home_stats/', views.home_stats, name='home_stats'),
    path('home_rt_country/', views.home_rt_country, name='home_rt_country'),
    path('home_analysis_for_prov/', views.home_analysis_for_prov, name='home_analysis_for_prov'),
    path('home_analysis_sa/', views.home_analysis_sa, name='home_analysis_sa'),
    path('home_analysis_per_prov/', views.home_analysis_per_prov, name='home_analysis_per_prov'),
    path('home_daily_sa/', views.home_daily_sa, name='home_daily_sa'),
    path('home_forecast/', views.home_forecast, name='home_forecast'),
    path('export/', views.export, name='export'),
    path('matplot/', views.matplot, name='matplot'),
    path('rtmodel1/', views.rtmodel1, name='rtmodel1'),
    path('snapshot/', views.snapshot, name='snapshot'),
]
