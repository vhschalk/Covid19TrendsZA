from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    #path('data/', views.data, name='data'),
    path('export/', views.export, name='export'),
    path('matplot/', views.matplot, name='matplot')
]
