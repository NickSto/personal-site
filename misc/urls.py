from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

app_name = 'misc'
urlpatterns = [
  url(r'^env/$', RedirectView.as_view(url='../env', permanent=True)),
  url(r'^env$', views.env, name='env'),
  url(r'^userinfo/$', RedirectView.as_view(url='../userinfo', permanent=True)),
  url(r'^userinfo$', views.userinfo, name='userinfo'),
  url(r'^setcookie/$', RedirectView.as_view(url='../setcookie', permanent=True)),
  url(r'^setcookie$', views.setcookie, name='setcookie'),
  url(r'^export/$', RedirectView.as_view(url='../export', permanent=True)),
  url(r'^export$', views.export, name='export'),
]