from __future__ import division
from __future__ import unicode_literals

import codecs
import os

from django.contrib.auth import logout as logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import Context
from django.template import RequestContext
from django.template import loader
from django.template.defaultfilters import slugify

from templatetags.docutils_extensions.utils import make_pdf

from models import *

def render_to_response(request, template, context):
    c = RequestContext(request, context)
    t = loader.get_template(template)
    return HttpResponse(t.render(c))

def core_index(request):
    classrooms = Classroom.objects.all()
    active_classrooms = classrooms.filter(is_active=True)
    
    context = {
        'classrooms': classrooms,
        'active_classrooms': active_classrooms,
    }
    template = 'core/index.html'
    
    c = RequestContext(request, context)
    t = loader.get_template(template)
    
    return HttpResponse(t.render(c))


def core_logout(request):
    logout(request)
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect('page_root')


def show_page(request, url='/'):            
    try:
        page = Page.objects.get(url=url)
        if page.access_level == 1 and not request.user.is_active:
            assert False
        if page.access_level == 2 and not request.user.is_staff:
            assert False
        page.update()
        # page.children.exclude(access_level=2)
        # page.children.exclude(access_level=1)
        context = {
            'page' : page,
        }
        template = 'core/show.html'
    except:
        if request.user.is_staff:
            return redirect('edit_page', url)
        else:
            context = {
                'page': url,
            }
            template = 'core/404.html'

    return render_to_response(request, template, context)


# @login_required(login_url=reverse('page_login')) # not sure why this doesn't work....
@login_required(login_url='/core/login/')
def edit_page(request, url='/'):
    try:
        page = Page.objects.get(url=url)
    except: # we still have to pass 'url' to the template...
        page = { 'url': url }

    template = 'core/edit.html'
    context = {
        'page' : page,
    }
    return render_to_response(request, template, context)


def post_page(request):
    if request.user.is_staff and request.method == 'POST':
        url = request.POST['url'] + '/'
        url = url.replace('//', '/')
        
        if 'cancel' in request.POST:
            return redirect('show_page', url)

        try:
            page = Page.objects.get(url=url)
        except:
            page = Page(url=url)
            page.save()
            
        if 'delete' in request.POST:
            parent = page.parent
            page.delete()
            if parent:
                return redirect('show_page', parent.url)
            else:
                return redirect('root_page')
        
        new_url = request.POST['new_url'] + '/'
        new_url = new_url.replace('//', '/')
        # new_url = re.sub('[^\w^\/]+', '', new_url) # poor man's validation attempt
        content = request.POST['content']
        content = content.replace('\r\n','\n')

        if 'update' in request.POST or 'submit' in request.POST:
            page.url = new_url
            page.content = content
            page.save()
            if 'update' in request.POST:
                return redirect('edit_page', page.url)
            else:
                return redirect('show_page', page.url)

    # nothing should ever get here...
    return redirect('root_page')
    
    
def ppdf_page(request, url=''):
    try:        
        page = Page.objects.get(url=url)
    except:
        return redirect('page_show', url)

    context = {
        'page' : page,
    }
    template = 'core/ppdf.tex'

    c = Context(context,autoescape=False)
    t = loader.get_template(template)
    latex = t.render(c)

    pdfname = make_pdf(latex, repeat=2)
    pdffile = open(pdfname, 'rb')
    outfile = '%s.pdf' % slugify(page.title)
    response = HttpResponse(pdffile.read(), content_type='application/pdf')
    # response['Content-disposition'] = 'attachment; filename=%s' % outfile

    return response
