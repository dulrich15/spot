from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.core_index, name='core_index'),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'core/login.html'}, name='core_login'),
    url(r'^logout/$', views.core_logout, name='core_logout'),

    url(r'^root/$', views.show_page, name='root_page'),

    url(r'^show(?P<url>(/[\w\-/]*))$', views.show_page, name='show_page'),
    url(r'^edit(?P<url>(/[\w\-/]*))$', views.edit_page, name='edit_page'),
    url(r'^ppdf(?P<url>(/[\w\-/]*))$', views.ppdf_page, name='ppdf_page'),

    url(r'^post/$', views.post_page, name='post_page'),
]
