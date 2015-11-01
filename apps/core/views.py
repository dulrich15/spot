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


def get_restriction_level(request):
    if request.user.is_staff:
        restriction_level = 2
    elif request.user.is_authenticated():
        restriction_level = 1
    else:
        restriction_level = 0
    return restriction_level


def get_page(url, request):
    # try:
    if 1==1:
        page = Page.objects.get(url=url)
        page.update()
        
        access_level = get_restriction_level(request)
        
        page.down_list = []
        for child in page.children:
            if access_level >= child.restriction_level:
                page.down_list.append(child)
    
                child.down_list = []
                for grandchild in child.children:
                    if access_level >= grandchild.restriction_level:
                        child.down_list.append(grandchild)
    
        if page.parent:

            page.side_list = []
            for sibling in page.parent.children:
                if access_level >= sibling.restriction_level:
                    # if page.classroom and sibling.classroom is not None:
                    if 1==1:
                        page.side_list.append(sibling)

            if page.series_member:
                i = page.side_list.index(page)
                if i < len(page.side_list) - 1:
                    page.next = page.side_list[i + 1]
                if i > 0:
                    page.prev = page.side_list[i - 1]
            else:
                page.side_list.remove(page)
    
    # except:
    #     page = None
        
    return page


def core_index(request):
    classrooms = Classroom.objects.all()
    active_classrooms = []
    for classroom in Classroom.objects.all():
        if classroom.is_active:
            active_classrooms.append(classroom)
            
    context = {
        'classrooms': classrooms,
        'active_classrooms': active_classrooms,
    }
    template = 'core/page_index.html'
    
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
    page = get_page(url, request)

    access_level = get_restriction_level(request)

    redirect_page = False
    if page is None:
        redirect_page = True
    elif access_level < page.restriction_level:
        redirect_page = True

    if redirect_page:
        if request.user.is_staff:
            return redirect('edit_page', url)
        else:
            context = { 'page': url }
            template = 'core/page_404.html'
            return render_to_response(request, template, context)

    context = {
        'page' : page,
        'restriction_level': get_restriction_level(request),
    }
    if request.session.get('show_full', False):
        template = 'core/show_full.html'
    else:
        template = 'core/show_page.html'

    return render_to_response(request, template, context)


# @login_required(login_url=reverse('page_login')) # not sure why this doesn't work....
@login_required(login_url='/core/login/')
def edit_page(request, url='/'):
    try:
        page = Page.objects.get(url=url)
    except: # we still have to pass 'url' to the template...
        page = { 'url': url }

    template = 'core/edit_page.html'
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
            page.raw_content = content
            page.save()
            if 'update' in request.POST:
                return redirect('edit_page', page.url)
            else:
                return redirect('show_page', page.url)

    # nothing should ever get here...
    return redirect('root_page')
    
    
def prnt_page(request, url=''):
    page = get_page(url, request)

    context = {
        'page' : page,
    }
    template = 'core/{}'.format(page.print_template)
    c = Context(context, autoescape=False)
    t = loader.get_template(template)

    latex = t.render(c)

    pdfname = make_pdf(latex, repeat=2)
    pdffile = open(pdfname, 'rb')
    outfile = '%s.pdf' % slugify(page.title)
    response = HttpResponse(pdffile.read(), content_type='application/pdf')
    # response['Content-disposition'] = 'attachment; filename=%s' % outfile

    return response


def show_full(request, url):
    request.session['show_full'] = not(request.session.get('show_full', False))
    return redirect('show_page', url)
