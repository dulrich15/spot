from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

# from django.views.generic.base import TemplateView
# from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^index/$', TemplateView.as_view(template_name='website_index.html')),
    url(r'^', include('spot.apps.core.urls')),
]
