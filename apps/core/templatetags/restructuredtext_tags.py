from __future__ import division
from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

from docutils.core import publish_parts

from docutils_extensions import writers
from docutils_extensions.directives import get_latex_path

register = template.Library()

@register.filter(is_safe=True)
def rst2html(source, initial_header=2, inline=False):
    return writers.rst2html(source, initial_header, inline)

@register.filter(is_safe=True)
def rst2html_inline(source, initial_header=2, inline=True):
    return writers.rst2html(source, initial_header, inline)

@register.filter(is_safe=True)
def rst2latex(source, initial_header=-1):
    return writers.rst2latex(source, initial_header)

@register.filter(is_safe=True)
def latex_path(filepath):
    return mark_safe(get_latex_path(filepath))
