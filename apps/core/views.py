from __future__ import division
from __future__ import unicode_literals

import codecs
import os
import re

from django.contrib import messages
from django.contrib.auth import logout as logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
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


def get_bg_color(request):
    if request.user.is_staff:
        return '#f1e8e8'
    elif request.user.is_active:
        return '#ffffe0'
    else:
        return '#ffffff'


def get_restriction_level(request):
    if request.user.is_staff:
        restriction_level = 2
    elif request.user.is_authenticated():
        restriction_level = 1
    else:
        restriction_level = 0
    return restriction_level


def get_page(url, request):
    try:
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
                    # if page is a classroom, only show related classrooms
                    # if page.classroom is None or sibling.classroom is not None:
                    if 1==1: # no, show all ...
                        page.side_list.append(sibling)

            if page.series_member:
                i = page.side_list.index(page)
                if i < len(page.side_list) - 1:
                    page.next = page.side_list[i + 1]
                if i > 0:
                    page.prev = page.side_list[i - 1]
            else:
                page.side_list.remove(page)
    
    except:
        page = None
        
    return page


def logged_in_message(sender, user, request, **kwargs):
    messages.info(request, "Hi {}, you are now logged in.".format(request.user.first_name, request.user.username))
user_logged_in.connect(logged_in_message)


def core_logout(request):
    logout(request)
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect('page_root')


def core_index(request):
    try:
        classroom = Classroom.objects.filter(is_active=True).order_by('-first_date')[0]
        page = classroom.home_page
        return redirect('show_page', page.url)

    except:
        if request.user.is_staff:
            return redirect('show_page', '/')
        else:
            context = { 'page': '/' }
            template = 'core/page_404.html'
        return render_to_response(request, template, context)


def list_classrooms(request):
    classrooms = Classroom.objects.all()
    active_classrooms = []
    for classroom in Classroom.objects.all():
        if classroom.is_active:
            active_classrooms.append(classroom)

    context = {
        'classrooms': classrooms,
        'active_classrooms': active_classrooms,
        'bg_color': get_bg_color(request),
    }
    template = 'core/list_classrooms.html'

    c = RequestContext(request, context)
    t = loader.get_template(template)
    
    return HttpResponse(t.render(c))


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
        'bg_color': get_bg_color(request),
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
    
    
def print_page(request, url=''):
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


def list_students(request, classroom_slug):
    if not request.user.is_staff:
        return redirect('show_page', classroom_slug)

    try:
        classroom = Classroom.objects.get(slug=classroom_slug)
    except:
        return redirect('core_index')

    context = {
        'classroom': classroom,
        'bg_color': get_bg_color(request),
    }
    template = 'core/list_students.html'

    c = RequestContext(request, context)
    t = loader.get_template(template)

    return HttpResponse(t.render(c))


def edit_student_list(request, classroom_slug):
    if not request.user.is_staff:
        return redirect('show_page', classroom_slug)

    try:
        classroom = Classroom.objects.get(slug=classroom_slug)
    except:
        return redirect('core_index')

    students = Student.objects.filter(classroom=classroom)
    student_list_csv = ''
    for student in students:
        student_csv = ','.join([student.last_name,student.first_name,''])
        student_list_csv += student_csv + '\n'

    context = {
        'student_list_csv': student_list_csv,
        'classroom': classroom,
        'bg_color': get_bg_color(request),
    }
    template = 'core/edit_student_list.html'

    c = RequestContext(request, context)
    t = loader.get_template(template)

    return HttpResponse(t.render(c))


def post_student_list(request, classroom_slug):
    if not request.user.is_staff:
        return redirect('show_page', classroom_slug)

    try:
        classroom = Classroom.objects.get(slug=classroom_slug)
    except:
        return redirect('core_index')

    students = Student.objects.filter(classroom=classroom)

    if 'submit' in request.POST:

        for student in students: # really should only delete those not in POST...
            student.delete()

        student_list = request.POST['student_list_csv'].splitlines()
        for line in student_list:
            [last_name, first_name, password] = [x.strip() for x in line.split(',')]

            username = first_name[0].lower()
            username += re.sub(r'[^a-z]', '', last_name.lower())[:7]

            try:
                student_user = User.objects.get(username=username)
            except:
                student_user = User()
                student_user.username = username
                student_user.last_name = last_name
                student_user.first_name = first_name
                student_user.set_password(password)
                student_user.save()

            student = Student()
            student.classroom = classroom
            student.user = student_user
            student.save()

            student_user.first_name = first_name
            student_user.last_name = last_name
            student_user.save()

    return redirect('list_students', classroom_slug)

