from __future__ import division
from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

from docutils.core import publish_parts

from docutils_extensions import utils

## -------------------------------------------------------------------------- ##

register = template.Library()

@register.filter(is_safe=True)
def rst2html(source, initial_header=2, inline=False):
    return utils.rst2html(source, initial_header, inline)

@register.filter(is_safe=True)
def rst2html_inline(source, initial_header=2, inline=True):
    return utils.rst2html(source, initial_header, inline)

@register.filter(is_safe=True)
def rst2latex(source, initial_header=-1):
    return utils.rst2latex(source, initial_header)
