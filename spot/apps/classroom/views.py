from __future__ import division
from __future__ import unicode_literals

from django.http import HttpResponse
from django.template import RequestContext
from django.template import loader

from models import *

def list_classrooms(request):
    classrooms = Classroom.objects.all()
    active_classrooms = classrooms.filter(is_active=True)
    
    context = {
        'classrooms': classrooms,
        'active_classrooms': active_classrooms,
    }
    template = 'list_classrooms.html'
    
    c = RequestContext(request, context)
    t = loader.get_template(template)
    
    return HttpResponse(t.render(c))


def show_classroom(request, slug):
    classroom = Classroom.objects.get(slug=slug)
    
    context = {
        'classroom': classroom,
    }
    template = 'show_classroom.html'
    
    c = RequestContext(request, context)
    t = loader.get_template(template)
    
    return HttpResponse(t.render(c))

