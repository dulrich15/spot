from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.core_index, name='core_index'),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'core/page_login.html'}, name='core_login'),
    url(r'^logout/$', views.core_logout, name='core_logout'),

    url(r'^classrooms/$', views.list_classrooms, name='show_classrooms'),

    url(r'^show/$', views.show_page, name='root_page'),

    url(r'^show(?P<url>(/([\w\-]+/)*))$', views.show_page, name='show_page'),
    url(r'^full(?P<url>(/([\w\-]+/)*))$', views.show_full, name='show_full'),
    url(r'^print(?P<url>(/([\w\-]+/)*))$', views.print_page, name='print_page'),
    url(r'^edit(?P<url>(/([\w\-]+/)*))$', views.edit_page, name='edit_page'),
    url(r'^post/$', views.post_page, name='post_page'),

    url(r'^full(?P<url>(/([\w\-]+/)*))$', views.show_full, name='show_full'),

    url(r'^students/(\w+)/$', views.list_students, name='list_students'),
    url(r'^students/(\w+)/edit/$', views.edit_student_list, name='edit_student_list'),
    url(r'^students/(\w+)/post/$', views.post_student_list, name='post_student_list'),
]
