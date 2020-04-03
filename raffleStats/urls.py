from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^(?P<vpost_id>[0-9a-zA-Z]{6})/$', views.details, name='details'),
    url(r'^api/spotcounts/(?P<vpost_id>[0-9a-zA-Z]{6})/$', views.spotcounts, name='spotcounts'),
]
