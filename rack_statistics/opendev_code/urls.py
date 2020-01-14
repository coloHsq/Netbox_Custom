from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'opendev'

urlpatterns = [

    path(r'rackstats/', views.RackStats.as_view(), name='rackStats'),
]
