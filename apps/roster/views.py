from __future__ import division
from __future__ import unicode_literals

import re

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext
from django.template import loader

from models import *
from apps.core.views import get_bg_color


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
    template = 'roster/list_students.html'

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
    template = 'roster/edit_student_list.html'

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


