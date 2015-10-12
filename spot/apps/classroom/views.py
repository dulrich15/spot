from __future__ import division
from __future__ import unicode_literals

from django.http import HttpResponse

def show_home(request):
    return HttpResponse('Hello world!')