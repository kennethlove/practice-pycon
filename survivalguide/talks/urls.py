from __future__ import absolute_import

from django.conf.urls import patterns, url, include

from . import views


lists_patterns = patterns(
    '',
    url(r'^$', views.TalkListListView.as_view(), name='list'),
    url(r'^d/(?P<slug>[-\w]+)/$', views.TalkListDetailView.as_view(),
        name='detail'),
    url(r'^create/$', views.TalkListCreateView.as_view(), name='create'),
)

urlpatterns = patterns(
    '',
    url(r'^lists/', include(lists_patterns, namespace='lists')),
)
