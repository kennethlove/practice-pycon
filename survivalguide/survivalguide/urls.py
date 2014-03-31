from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from django.contrib import admin

from .views import SignUpView, LoginView, HomePageView, LogoutView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^talks/', include('talks.urls', namespace='talks')),
    url(r'^accounts/register/$', SignUpView.as_view(), name='signup'),
    url(r'^accounts/login/$', LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomePageView.as_view(), name='home'),
)

