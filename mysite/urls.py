"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
import traffic.views
import pages.views

urlpatterns = [
  # url(r'^admin/', include(admin.site.urls)),
  url(r'^misc/', include('misc.urls')),
  url(r'^traffic$', traffic.views.monitor, name='traffic_monitor'),
  url(r'^yourgenome$', pages.views.yourgenome, name='pages_yourgenome'),
  url(r'^yourgenome/$', RedirectView.as_view(url='/yourgenome', permanent=True)),
  url(r'^pages/', include('pages.urls')),
  url(r'^traffic/', include('traffic.urls')),
  url(r'^admin/', include('myadmin.urls')),
  url(r'^wikihistory/', include('wikihistory.urls')),
  # If nothing else matches, send it to notepad.
  url(r'', include('notepad.urls')),
]
