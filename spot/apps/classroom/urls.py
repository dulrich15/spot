from django.conf.urls import patterns, include, url

urlpatterns = patterns('spot.apps.classroom.views',
    url(r'^$', 'show_home', name='show_home'),
)
