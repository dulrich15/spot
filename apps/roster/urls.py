from django.conf.urls import url

import views

urlpatterns = [
    url(r'^roster/(\w+)/$', views.list_students, name='list_students'),
    url(r'^roster/(\w+)/edit/$', views.edit_student_list, name='edit_student_list'),
    url(r'^roster/(\w+)/post/$', views.post_student_list, name='post_student_list'),
]


