from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grades', include('spot.apps.gradebook.urls')),
    url(r'^', include('spot.apps.classroom.urls')),
)
