from __future__ import division
from __future__ import unicode_literals

import codecs
import os
import xml.etree.ElementTree as ET

from subprocess import Popen
from subprocess import PIPE

from django.utils.safestring import mark_safe

from docutils.core import publish_parts
from docutils.writers import latex2e

from apps.core.config import LATEX_CMD

from directives import LATEX_WORK_PATH

def make_pdf(latex, repeat=1):

    curdir = os.getcwd()
    os.chdir(LATEX_WORK_PATH)

    basename = 'temp'

    for ext in ['idx','ind','ilg','aux','log','out','toc','tex','pdf','png']:
        try:
            os.remove('{}.{}'.format(basename, ext))
        except:
            pass

    texname = '{}.tex'.format(basename)
    idxname = '{}.idx'.format(basename)
    pdfname = '{}.pdf'.format(basename)

    texfile = codecs.open(texname, 'w', 'utf-8')
    texfile.write(latex)
    texfile.close()

    for i in range(repeat):
        cmd = os.path.join(LATEX_CMD, 'pdflatex')
        cmd = [cmd, '--interaction=nonstopmode', texname]
        p = Popen(cmd,stdout=PIPE,stderr=PIPE)
        out, err = p.communicate()

    try:
        open(idxname)
        if os.path.getsize(idxname):

            cmd = os.path.join(LATEX_CMD, 'makeindex')
            cmd = [cmd,  idxname]
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()

            cmd = os.path.join(LATEX_CMD, 'pdflatex')
            cmd = [cmd, '--interaction=nonstopmode', texname]
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
    except:
        pass

    os.chdir(curdir)

    # assert False
    
    return os.path.join(LATEX_WORK_PATH, pdfname)
    
