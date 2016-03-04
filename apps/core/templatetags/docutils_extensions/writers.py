from __future__ import division
from __future__ import unicode_literals

# look here for improvements...
# http://www.arnebrodowski.de/blog/write-your-own-restructuredtext-writer.html

import codecs
import os
import xml.etree.ElementTree as ET

from subprocess import Popen, PIPE

from django.utils.safestring import mark_safe

from docutils.core import publish_parts
from docutils.writers import latex2e

class MyLatexWriter(latex2e.Writer):

    def __init__(self, initial_header_level=1):
        latex2e.Writer.__init__(self)
        if initial_header_level == 2:
            self.translator_class = MyLatexTranslator2
        elif initial_header_level == 1:
            self.translator_class = MyLatexTranslator1
        else:
            self.translator_class = MyLatexTranslator0


class MyLatexTranslator2(latex2e.LaTeXTranslator):
    section_level = 2

    def __init__(self, node):
        latex2e.LaTeXTranslator.__init__(self, node)
        self._section_number = self.section_level*[0]


class MyLatexTranslator1(latex2e.LaTeXTranslator):
    section_level = 1

    def __init__(self, node):
        latex2e.LaTeXTranslator.__init__(self, node)
        self._section_number = self.section_level*[0]


class MyLatexTranslator0(latex2e.LaTeXTranslator):
    section_level = 0

    def __init__(self, node):
        latex2e.LaTeXTranslator.__init__(self, node)
        self._section_number = self.section_level*[0]


def rst2xml(source, part='whole'):
    source = '.. default-role:: math\n\n' + source
    writer_name = 'xml'        
    settings_overrides = {}
    
    text = publish_parts(
        source=source, 
        writer_name=writer_name,
        settings_overrides=settings_overrides,
    )[part].strip()

    root = ET.fromstring(text.encode('utf-8'))
    return root


def rst2html(source, initial_header_level=2, inline=False, part='body'):
    
    source = '.. default-role:: math\n\n' + source
    writer_name = 'html'        
    settings_overrides = {
        'compact_lists' : True,
        'footnote_references' : 'superscript',
        'math_output' : 'MathJax',
        'stylesheet_path' : None,
        'initial_header_level' : initial_header_level,
        # 'doctitle_xform' : 0,
    }

    html = publish_parts(
        source=source,
        writer_name=writer_name,
        settings_overrides=settings_overrides,
    )[part].strip()

    if inline:
        if html[:3] == '<p>' and html[-4:] == '</p>':
            html = html[3:-4]
        
    html = html.replace('...','&hellip;')
    html = html.replace('---','&mdash;')
    html = html.replace('--','&ndash;')
    # oops ... need to reverse these back
    html = html.replace('<!&ndash;','<!--')
    html = html.replace('&ndash;>','-->')

    return mark_safe(html)
    

def rst2latex(source, initial_header_level=-1, part='body'):
    source = '.. default-role:: math\n\n' + source
    writer = MyLatexWriter(initial_header_level)
    settings_overrides = {
        'use_latex_docinfo': True,
    }
    
    latex = publish_parts(
        source=source,
        writer=writer,
        settings_overrides=settings_overrides,
    )[part]
    latex = latex.replace('-{}','-') # unwind this manipulation from docutils

    return latex.strip()
