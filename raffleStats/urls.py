from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('history', views.history, name='history'),
    url(r'^(?P<vpost_id>[0-9a-zA-Z]{6})/$', views.details, name='details'),
    url(r'^api/spotcounts/(?P<vpost_id>[0-9a-zA-Z]{6})/$', views.spotcounts, name='spotcounts'),
    url(r'^dataset/(?P<vfrom_date>[0-9]{2}/[0-9]{2}/[0-9]{4})-(?P<vto_date>[0-9]{2}/[0-9]{2}/[0-9]{4})/$', views.dataset, name="dataset"),
]
