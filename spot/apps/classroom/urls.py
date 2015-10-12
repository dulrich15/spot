from django.conf.urls import url

from views import *

urlpatterns = [
    url(r'^$', list_classrooms, name='list_classrooms'),
    url(r'^(\w+)/$', show_classroom, name='show_classroom'),
]
