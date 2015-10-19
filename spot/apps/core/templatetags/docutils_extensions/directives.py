from __future__ import division
from __future__ import unicode_literals

import codecs
import hashlib
import json
import os
import posixpath
import random
import re
import shutil
import yaml

from subprocess import Popen, PIPE
from PIL import Image

from django.core.urlresolvers import reverse

from docutils import nodes
from docutils.parsers import rst

from spot.apps.core.config import LATEX_CMD
from spot.apps.core.config import GS_CMD
from spot.apps.core.config import PYTHON_CMD
from spot.apps.core.config import FFMPEG_CMD

from spot.apps.core.config import IMAGE_URL
from spot.apps.core.config import IMAGE_PATH

from spot.apps.core.config import SYSGEN_URL
from spot.apps.core.config import SYSGEN_PATH

from writers import rst2html
from writers import rst2latex

WORK_PATH = '' # right here...
WORK_PATH = os.path.join(os.path.dirname(os.path.abspath( __file__ )), WORK_PATH)

LATEX_WORK_PATH = os.path.join(WORK_PATH, 'latex', '_')
MATHPLOTLIB_WORK_PATH = os.path.join(WORK_PATH, 'mathplotlib', '_')

def get_latex_path(filename):
    filename = filename.split(os.path.sep)
    for i in range(len(filename)):
        if ' ' in filename[i]:
            filename[i] = '"%s"' % filename[i]
    filename = '/'.join(filename)
    return filename

FIG_TEMPLATE = {
'default' : r'''
\begin{center}
%(figtext)s
%(caption)s
%(label)s
\end{center}
'''
,
'left' : r'''
%(figtext)s
%(caption)s
%(label)s
'''
,
'side' : r'''
\marginpar{
\vspace{%(offset)s}
\vspace{0.1in}
\centering
%(figtext)s
%(caption)s
%(label)s
}
'''
,
'sidecap' : r'''
\vspace{0.1in}
\begin{adjustwidth}{}{\adjwidth}
\begin{minipage}[c]{\picwidth}
\centering
%(figtext)s
\end{minipage}
\hfill
\begin{minipage}[c]{\capwidth}
%(caption)s
%(label)s
\end{minipage}
\end{adjustwidth}
\vspace{0.1in}
'''
,
'full' : r'''
\vspace{0.1in}
\begin{adjustwidth}{}{\adjwidth}
\centering
%(figtext)s
%(caption)s
%(label)s
\end{adjustwidth}
\vspace{0.1in}
'''
}

# Note the `everymath` statement below. This switches the default behavior of 
# inline math to display style. For *figures* I am constantly enforcing display
# mode, so this seems like a better default for my purpose. Use `textstyle` to 
# get the regular behavior, e.g., "\textstyle \int x dx = \frac{1}{2} x^2"
LATEX_TEMPLATE = r'''
\documentclass{article}
\pagestyle{empty}
\u005Cusepackage[active,tightpage]{preview}
\u005Cusepackage{p200}
\everymath{\displaystyle}
\renewcommand{\arraystretch}{1.5}
\renewcommand{\tabcolsep}{0.2cm}
\begin{document}
\begin{preview}
%s
\end{preview}
\end{document}
'''

MATPLOTLIB_TEMPLATE = r'''
from __future__ import division

import matplotlib
import numpy as np
import matplotlib.pyplot as plt

# matplotlib.rcParams['xtick.direction'] = 'out'
# matplotlib.rcParams['ytick.direction'] = 'out'

%s

plt.savefig('temp.png')
'''

MATPLOTLIB_ANI_TEMPLATE = r'''
from __future__ import division

import numpy as np
from numpy import sin, cos

from scipy import integrate
from scipy.fftpack import fft,ifft
from scipy.spatial.distance import pdist, squareform

from matplotlib import pyplot as plt
from matplotlib import animation

fig = plt.figure()

%s

ani = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=True)
ani.save('temp.mp4', fps=30, extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
'''

class fig_directive(rst.Directive):
    """
    ---------------------------
    Docutils directive: ``fig``
    ---------------------------

    Inserts a figure. Originally designed to support TikZ pictures. But one
    could pass any raw LaTeX code through.

    Example
    -------

    ::

        .. fig:: Some image here
            :image: image-filename.png
            :scale: 0.75

        .. fig:: Sample Trapezoid
            :position: side
            :label: trapezoid

            \begin{tikzpicture}
            \draw [fill=black!10] (-1,0.7) -- (1,0.7)
            -- (0.7,-0.7) -- (-0.7,-0.7) -- cycle;
            \end{tikzpicture}

    Options
    -------

    :image:     Used to insert images. Any content will be ignored. A label
                will be inserted with the image's filename.
    :scale:     Used to scale the image.
    :label:     Used for hyperlinks references. See ``fig`` role.
    :position:  Used to position figure within document. There are three
                possible values:

                :inline:    Placement within flow of text [default].
                :side:      Placement in side margin.
                :full:      Used for large figures---will not respect
                            margins but will center across the full page.

    Notes
    -----

    * Must have content. Will be wrapped by begin and end statements.
    * Argument used for figure caption (optional).
    * If the image option is used, the label defaults to image name.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'image'     : rst.directives.unchanged,
        'scale'     : rst.directives.unchanged,
        'label'     : rst.directives.unchanged,
        'position'  : rst.directives.unchanged,
        'offset'    : rst.directives.unchanged,
        }
    has_content = True

    def run(self):

        node_list = []

        try:
            scale = float(self.options['scale'])
        except:
            scale = 1.00

        if 'position' in self.options.keys():
            position = self.options['position']
        else:
            position = 'default'

# LaTeX writer specifics start (offset is ignored for HTML writer)

        if 'offset' in self.options.keys():
            offset = self.options['offset']
        else:
            offset = '0pt'

        if self.arguments:
            caption = rst2latex(self.arguments[0])
            caption = r'\captionof{figure}{%s}' % caption
        else:
            caption = ''

        if 'label' in self.options.keys():
            label = nodes.make_id(self.options['label'])
            label = r'\label{fig:%s}' % label
        else:
            label = ''

        if 'image' in self.options.keys():
            image = self.options['image']

            if str(image).rsplit('.',1)[1] in ['png','jpg','gif','pdf']:

                check_path = os.path.join(IMAGE_PATH, image)
                check_path = os.path.normpath(check_path)

                if not os.path.exists(check_path):
                    print 'Could not locate "%s"' % check_path

                latex_path = get_latex_path(check_path)

                figtext = r'\includegraphics[scale=%s]{%s}'
                figtext = figtext % (scale, latex_path)
                if not label:
                    label = nodes.make_id(image)
                    label = r'\label{fig:%s}' % label
            else:
                figtext = image
        else:
            # cf. note over LATEX_TEMPLATE
            figtext = '\n\\everymath{\\displaystyle}\n'
            figtext += '\n'.join(self.content)
            figtext += '\n\\everymath{\\textstyle}\n'

        text = FIG_TEMPLATE[position] % {
            'offset'    : offset,
            'caption'   : caption,
            'label'     : label,
            'figtext'   : figtext,
            }

        node = nodes.raw(text=text, format='latex', **self.options)
        node_list += [node]

# HTML writer specifics start...

        if 'image' in self.options.keys():
            image = self.options['image']

            check_path = os.path.join(IMAGE_PATH, image)
            check_path = os.path.normpath(check_path)

            if os.path.exists(check_path):
                img_width, img_height = Image.open(check_path).size
                fig_width = int(img_width*scale*1.00)

                if 'label' in self.options.keys():
                    label = nodes.make_id(self.options['label'])
                else:
                    label = nodes.make_id(image)

                figtext = '\n'
                if 'side' in position:
                    # figtext += '<div id="fig:{0}" class="my-docutils fig {1}" style="width:{2}px;">\n'
                    figtext += '<div id="fig:{0}" class="my-docutils fig {1}">\n'
                else:
                    figtext += '<div id="fig:{0}" class="my-docutils fig {1}">\n'
                    # figtext += '<div id="fig:{0}" class="my-docutils fig {1}" style="width:{2}px;">\n'
                figtext = figtext.format(label, position, fig_width)

                html_path = posixpath.join(IMAGE_URL, image)
                figtext += '<a href="{0}"><img width="{1}px" src="{0}"></a>\n'.format(html_path, fig_width)
                # figtext += '<a href="{0}"><img src="{0}"></a>\n'.format(html_path, fig_width)

                if self.arguments:
                    figtext += rst2html(self.arguments[0])

                figtext += '</div>\n'

            else:
                print 'Could not locate "%s"' % check_path
                figtext = '\n<div class="my-docutils-error">\n<p>Missing image</p>\n</div>\n'

        else: # try to construct the image
            # Unlike a normal image, our reference will come from the content...
            content = '\n'.join(self.content)#.replace('\\\\','\\')
            image_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            image_name = '%s.png' % image_hash
            image_path = os.path.join(SYSGEN_PATH, 'latex', image_name)
            image_url = posixpath.normpath(os.path.join(SYSGEN_URL, 'latex', image_name))
            self.options['uri'] = image_url

            # try:
            if 1==1:
                # Maybe we already made it? If not, make it now...
                if not os.path.isfile(image_path):

                    print 'Making image %s' % image_name

                    # Set up our folders and filename variables
                    curdir = os.getcwd()

                    # Write the LaTeX file to the image folder
                    os.chdir(LATEX_WORK_PATH)
                    f = codecs.open('temp.tex', 'w', 'utf-8')
                    f.write(LATEX_TEMPLATE % content)
                    f.close()

                    # Run LaTeX ...
                    cmd = os.path.join(LATEX_CMD, 'pdflatex')
                    cmd = [cmd,
                    '--interaction=nonstopmode',
                    'temp.tex'
                    ]
                    p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                    out, err = p.communicate()

                    cmd = [GS_CMD,
                    '-q',
                    '-dBATCH',
                    '-dNOPAUSE',
                    '-sDEVICE=png16m',
                    '-r600',
                    '-dTextAlphaBits=4',
                    '-dGraphicsAlphaBits=4',
                    '-sOutputFile=temp.png',
                    'temp.pdf',
                    ]
                    p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                    out, err = p.communicate()

                    img = Image.open('temp.png')
                    img_scale = 0.40 * scale
                    print img_scale
                    img_width = int(img_scale * img.size[0])
                    img_height = int(img_scale * img.size[1])
                    img = img.resize((img_width, img_height), Image.ANTIALIAS)
                    img.save('temp.png', 'png')

                    # Finally, move the image file and clean up
                    image_dir = os.path.dirname(image_path)
                    if not os.path.exists(image_dir):
                        os.makedirs(image_dir)
                    shutil.copyfile('temp.png', image_path)
                    os.chdir(curdir)

                self.options['alt'] = self.content

                img_width, img_height = Image.open(image_path).size
                fig_width = int(img_width*scale*0.50)

                if 'label' in self.options.keys():
                    label = nodes.make_id(self.options['label'])
                else:
                    label = nodes.make_id(image_name)

                figtext = '\n'
                # figtext += '\n<div id="fig:{0}" class="my-docutils fig {1}" style="width:{2}px;">\n'
                figtext += '\n<div id="fig:{0}" class="my-docutils fig {1}">\n'
                figtext = figtext.format(label, position, fig_width)

                figtext += '<a href="{0}"><img width="{1}px" src="{0}"></a>\n'.format(image_url, fig_width)
                # figtext += '<a href="{0}"><img src="{0}"></a>\n'.format(image_url, fig_width)

                if self.arguments:
                    figtext += rst2html(self.arguments[0])

                figtext += '</div>\n'

            # except:
            #     print 'Could not locate "%s"' % image_path
            #     figtext = '\n<div class="my-docutils-error">\n<p>File generation error:</p>\n<pre>\n' + '\n'.join(self.content) + '</pre>\n</div>\n'

        text = figtext

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        return node_list

rst.directives.register_directive('fig', fig_directive)

class plt_directive(rst.Directive):
    """
    ---------------------------
    Docutils directive: ``plt``
    ---------------------------

    Inserts a matplotlib plot.

    Example
    -------

    ::

        .. plt:: Some numbers
            :label: test-plot

            plt.plot([1,2,3,4], [1,4,9,16], 'ro')
            plt.axis([0, 6, 0, 20])
            plt.ylabel('some numbers')

    Options
    -------

    :scale:     Used to scale the image.
    :label:     Used for hyperlinks references. See ``plt`` role.
    :position:  Used to position figure within document. There are three
                possible values:

                :inline:    Placement within flow of text [default].
                :side:      Placement in side margin.
                :full:      Used for large figures---will not respect
                            margins but will center across the full page.

    Notes
    -----

    * Must have content. Will be wrapped by begin and end statements.
    * Argument used for figure caption (optional).
    * If the image option is used, the label defaults to image name.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'scale'     : rst.directives.unchanged,
        'label'     : rst.directives.unchanged,
        'position'  : rst.directives.unchanged,
        'offset'    : rst.directives.unchanged,
        }
    has_content = True

    def run(self):

        node_list = []

        # Unlike a normal image, our reference will come from the content...
        content = '\n'.join(self.content)#.replace('\\\\','\\')

        # Have to have some serious protection here....
        if '\nimport' in content:
            assert False

        # Define image name and location
        image_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        image_name = '%s.png' % image_hash
        image_path = os.path.join(SYSGEN_PATH, 'matplotlib', image_name)
        image_url = posixpath.normpath(os.path.join(SYSGEN_URL, 'matplotlib', image_name))
        self.options['uri'] = image_url

        # Maybe we already made it? If not, make it now...
        if not os.path.isfile(image_path):

            print 'Making image %s' % image_name

            # Set up our folders and filename variables
            curdir = os.getcwd()

            # Write the matplotlib file to the temp folder
            os.chdir(MATHPLOTLIB_WORK_PATH)
            f = codecs.open('temp.py', 'w', 'utf-8')
            f.write(MATPLOTLIB_TEMPLATE % content)
            f.close()

            # Run matplotlib ...
            cmd = [PYTHON_CMD, 'temp.py']
            p = Popen(cmd,stdout=PIPE,stderr=PIPE)
            out, err = p.communicate()

            # Move the image file and clean up
            image_dir = os.path.dirname(image_path)
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            shutil.copyfile('temp.png', image_path)
            # os.remove('rm temp.*')
            os.chdir(curdir)

        try:
            scale = float(self.options['scale'])
        except:
            scale = 1.00

        if 'position' in self.options.keys():
            position = self.options['position']
        else:
            position = 'default'

        check_path = image_path

# LaTeX writer specifics start (offset is ignored for HTML writer)

        if 'offset' in self.options.keys():
            offset = self.options['offset']
        else:
            offset = '0pt'

        if self.arguments:
            caption = rst2latex(self.arguments[0])
            caption = r'\captionof{figure}{%s}' % caption
        else:
            caption = ''

        if 'label' in self.options.keys():
            label = nodes.make_id(self.options['label'])
            label = r'\label{plt:%s}' % label
        else:
            label = ''

        if os.path.exists(check_path):
            latex_path = get_latex_path(check_path)
            figtext = r'\includegraphics[scale=%s]{%s}'
            figtext = figtext % (scale*0.5, latex_path)
            if not label:
                label = nodes.make_id(image_name)
                label = r'\label{plt:%s}' % label
        else:
            print 'Could not locate "%s"' % check_path
            figtext = '\n'.join(self.content)

        text = FIG_TEMPLATE[position] % {
            'offset'    : offset,
            'caption'   : caption,
            'label'     : label,
            'figtext'   : figtext,
            }

        node = nodes.raw(text=text, format='latex', **self.options)
        node_list += [node]

# # HTML writer specifics start...

        if os.path.exists(check_path):
            img_width, img_height = Image.open(check_path).size
            fig_width = int(img_width*scale*0.75)

            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
            else:
                label = nodes.make_id(image_name)

            figtext = '\n'
            if 'side' in position:
                # figtext += '<div id="plt:{0}" class="my-docutils plt {1}" style="width:{2}px;">\n'
                figtext += '<div id="plt:{0}" class="my-docutils plt {1}">\n'
            else:
                figtext += '<div id="plt:{0}" class="my-docutils plt {1}">\n'
                # figtext += '<div id="plt:{0}" class="my-docutils plt {1}" style="width:{2}px;">\n'
            figtext = figtext.format(label, position, fig_width)

            figtext += '<a href="{0}"><img width="{1}px" src="{0}"></a>\n'.format(image_url, fig_width)
            # figtext += '<a href="{0}"><img src="{0}"></a>\n'.format(image_url, fig_width)

            if self.arguments:
                figtext += rst2html(self.arguments[0])

            figtext += '</div>\n'

        else:
            print 'Could not locate "%s"' % check_path
            figtext = '\n<div class="my-docutils-error">\n<p>File generation error:</p>\n<pre>\n' + '\n'.join(self.content) + '</pre>\n</div>\n'

        text = figtext

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        return node_list

rst.directives.register_directive('plt', plt_directive)

class ani_directive(rst.Directive):
    """
    ---------------------------
    Docutils directive: ``ani``
    ---------------------------

    Inserts a matplotlib animation.

    Example
    -------

    ::

        .. ani:: Wave motion
            :label: test-anim

            ax = plt.axes(xlim=(0, 2), ylim=(-2, 2))
            line, = ax.plot([], [], lw=2)

            # initialization function: plot the background of each frame
            def init():
                line.set_data([], [])
                return line,

            # animation function.  This is called sequentially
            def animate(i):
                x = np.linspace(0, 2, 1000)
                y = np.sin(2 * np.pi * (x - 0.01 * i))
                line.set_data(x, y)
                return line,

    Options
    -------

    :scale:     Used to scale the image.
    :label:     Used for hyperlinks references. See ``ani`` role.
    :position:  Used to position figure within document. There are three
                possible values:

                :inline:    Placement within flow of text [default].
                :side:      Placement in side margin.
                :full:      Used for large figures---will not respect
                            margins but will center across the full page.

    Notes
    -----

    * Must have content. Will be wrapped by begin and end statements.
    * Argument used for figure caption (optional).
    * If the image option is used, the label defaults to image name.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'scale'     : rst.directives.unchanged,
        'label'     : rst.directives.unchanged,
        'position'  : rst.directives.unchanged,
        'offset'    : rst.directives.unchanged,
        }
    has_content = True

    def run(self):

        node_list = []

        # Unlike a normal image, our reference will come from the content...
        content = '\n'.join(self.content)#.replace('\\\\','\\')

        # Have to have some serious protection here....
        if '\nimport' in content:
            assert False

        # Define image name and location
        image_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        image_name = '%s.mp4' % image_hash
        image_path = os.path.join(SYSGEN_PATH, 'matplotlib', image_name)
        image_url = posixpath.normpath(os.path.join(SYSGEN_URL, 'matplotlib', image_name))
        self.options['uri'] = image_url

        # Maybe we already made it? If not, make it now...
        if not os.path.isfile(image_path):

            print 'Making image %s' % image_name
            print image_path
            print image_url

            # Set up our folders and filename variables
            curdir = os.getcwd()

            # Write the matplotlib file to the temp folder
            os.chdir(MATHPLOTLIB_WORK_PATH)
            if os.path.isfile('temp.mp4'):
                os.remove('temp.mp4')

            f = codecs.open('temp.py', 'w', 'utf-8')
            f.write(MATPLOTLIB_ANI_TEMPLATE % content)
            f.close()

            # Run matplotlib ...
            cmd = [settings.PYTHON_CMD, 'temp.py']
            p = Popen(cmd,stdout=PIPE,stderr=PIPE)
            out, err = p.communicate()

            # Move the image file and clean up
            if os.path.isfile('temp.mp4'):
                image_dir = os.path.dirname(image_path)
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                shutil.copyfile('temp.mp4', image_path)

            os.chdir(curdir)

        try:
            scale = float(self.options['scale'])
        except:
            scale = 1.00

        if 'position' in self.options.keys():
            position = self.options['position']
        else:
            position = 'default'

        check_path = image_path

# LaTeX writer specifics start (offset is ignored for HTML writer)
### WILL THIS EVEN WORK FOR AN MP4 FILE ???

        if 'offset' in self.options.keys():
            offset = self.options['offset']
        else:
            offset = '0pt'

        if self.arguments:
            caption = rst2latex(self.arguments[0])
            caption = r'\captionof{figure}{%s}' % caption
        else:
            caption = ''

        if 'label' in self.options.keys():
            label = nodes.make_id(self.options['label'])
            label = r'\label{ani:%s}' % label
        else:
            label = ''

        if os.path.exists(check_path):
            latex_path = get_latex_path(check_path)
            figtext = r'\includegraphics[scale=%s]{%s}'
            figtext = figtext % (scale*0.5, latex_path)
            if not label:
                label = nodes.make_id(image_name)
                label = r'\label{ani:%s}' % label
        else:
            print 'Could not locate "%s"' % check_path
            figtext = '\n'.join(self.content)

        text = FIG_TEMPLATE[position] % {
            'offset'    : offset,
            'caption'   : caption,
            'label'     : label,
            'figtext'   : figtext,
            }

        node = nodes.raw(text=text, format='latex', **self.options)
        node_list += [node]

# # HTML writer specifics start...

        if os.path.exists(check_path):
            # img_width, img_height = Image.open(check_path).size
            # fig_width = int(img_width*scale*0.75)
            # fig_height = int(img_height*scale*0.75)

            # # From: http://stackoverflow.com/questions/7362130/getting-video-dimension-from-ffmpeg-i
            # # import subprocess, re
            # # pattern = re.compile(r'Stream.*Video.*([0-9]{3,})x([0-9]{3,})')

            # # def get_size(pathtovideo):
                # # p = subprocess.Popen(['ffmpeg', '-i', pathtovideo],
                                     # # stdout=subprocess.PIPE,
                                     # # stderr=subprocess.PIPE)
                # # stdout, stderr = p.communicate()
                # # match = pattern.search(stderr)
                # # if match:
                    # # x, y = map(int, match.groups()[0:2])
                # # else:
                    # # x = y = 0
                # # return x, y

            fig_width = 800
            fig_height = 600

            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
            else:
                label = nodes.make_id(image_name)

            figtext = '\n'
            if 'side' in position:
                # figtext += '<div id="ani:{0}" class="my-docutils ani {1}" style="width:{2}px;">\n'
                figtext += '<div id="ani:{0}" class="my-docutils ani {1}">\n'
            else:
                figtext += '<div id="ani:{0}" class="my-docutils ani {1}">\n'
                # figtext += '<div id="ani:{0}" class="my-docutils ani {1}" style="width:{2}px;">\n'
            figtext = figtext.format(label, position, fig_width)

            figtext += '<a href="{0}"><video width="{1}px" height="{2}px" controls><source src="{0}" type="video/mp4"></video></a>\n'.format(image_url, fig_width, fig_height)

            if self.arguments:
                figtext += rst2html(self.arguments[0])

            figtext += '</div>\n'

        else:
            print 'Could not locate "%s"' % check_path
            figtext = '\n<div class="my-docutils-error">\n<p>File generation error:</p>\n<pre>\n' + '\n'.join(self.content) + '</pre>\n</div>\n'

        text = figtext

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        return node_list

rst.directives.register_directive('ani', ani_directive)

class tbl_directive(rst.Directive):

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'label'        : rst.directives.unchanged,
        'cols'         : rst.directives.unchanged,
        'left-headers' : rst.directives.unchanged,
    }
    has_content = True

    def run(self):
        node_list = []
        
        self.assert_has_content()
        try:
            parser = rst.tableparser.GridTableParser()
            tbl = parser.parse(self.content)
        except:
            try:
                parser = rst.tableparser.SimpleTableParser()
                tbl = parser.parse(self.content)
            except:
                tbl = None

        if tbl:
            # parser.parse() returns a list of three items
            #
            # 1. A list of column widths
            # 2. A list of head rows
            # 3. A list of body rows

            colspecs = tbl[0]
            headrows = tbl[1] # tbl[1][i] is the ith column head
            bodyrows = tbl[2]

            # Each row contains a list of cells
            #
            # Each cell is either
            #
            # - None (for a cell unused because of another cell's span), or
            # - A tuple with four items:
            #
            #   1. The number of extra rows used by the cell in a vertical span
            #   2. The number of extra columns used by the cell in a horizontal span
            #   3. The line offset of the first line of the cell contents
            #   4. The cell contents --- a list of lines of text

        # Create html node
        
        text = ''
        if tbl:
            divid = ''
            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
                divid = ' id="tbl:{0}"'.format(label)

            caption = ''
            if self.arguments: # use as caption
                caption = rst2html(self.arguments[0], inline=True)

            colspec = len(colspecs) * 'c'
            if 'cols' in self.options.keys():
                colspec = re.sub('[^lcrLRC]', '', self.options['cols'])
            align = {'l': 'left', 'c': 'center', 'r': 'right'}

            left_headers = 0
            try:
                left_headers = int(self.options['left-headers'])
            except:
                pass
            
            text += '<div{} class="my-docutils tbl">\n'.format(divid)
            text += '<table>\n'

            for tag, rows in [('th', headrows), ('td', bodyrows)]:
                for row in rows:
                    text += '<tr>\n'
                    for cell in row:
                        if cell:
                            rowspan = ''
                            if cell[0]:
                                rowspan = ' rowspan="{}"'.format(cell[0] + 1)
                            colspan = ''
                            if cell[1]:
                                colspan = ' colspan="{}"'.format(cell[1] + 1)
                            
                            spec = colspec[row.index(cell)]                         
                            cellalign = align[spec.lower()]
                            celltext = rst2html('\n'.join(cell[3]), inline=True)

                            if row.index(cell) < left_headers:
                                this_tag = 'th'
                            else:
                                this_tag = tag
                                
                            if spec == spec.upper():
                                text += '<{}{}{} style="text-align:{};white-space:nowrap">\n'.format(this_tag, rowspan, colspan, cellalign)
                            else:
                                text += '<{}{}{} style="text-align:{}">\n'.format(this_tag, rowspan, colspan, cellalign)
                            text += '{}\n'.format(celltext)
                            text += '</{}>\n'.format(tag)
                    text += '</tr>\n'
            if caption:
                text += '<caption>{}</caption>\n'.format(caption)
            text += '</table>\n'
            text += '</div>\n'

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]
        
        # Create latex node
        
        text = ''
        if tbl:
            
            label = ''
            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
        
            caption = ''
            if self.arguments: # use as caption
                caption = rst2latex(self.arguments[0])

            colspec = len(colspecs) * 'c'
            if 'cols' in self.options.keys():
                colspec = self.options['cols'].lower()
        
            text += '\\begin{center}\n'

            if label:
                text += '\\label{{tbl:{0}}}\n'.format(label)
                
            text += '\\begin{{tabular}}{{{0}}}\n'.format(colspec)
            text += '\\hline\n'
            for row in headrows:
                celltext = []
                for cell in row:
                    if cell:
                        texlist = []
                        for x in cell[3]:
                            texlist.append('\\textbf{{{}}}'.format(rst2latex(x)))
                        celltext.append('\n'.join(texlist))
                    else:
                        celltext.append('')
                text += ' & '.join(celltext) + ' \\\\\n'
                text += '\\hline\n'
            for row in bodyrows:
                celltext = []
                for cell in row:
                    if cell:
                        texlist = []
                        for x in cell[3]:
                            if row.index(cell) < left_headers:
                                texlist.append('\\textbf{{{}}}'.format(rst2latex(x)))
                            else:
                                texlist.append(rst2latex(x))
                        celltext.append('\n'.join(texlist))
                    else:
                        celltext.append('')
                text += ' & '.join(celltext) + ' \\\\\n'
            text += '\\hline\n'
            text += '\\end{tabular}\n'

            if caption:
                text += '\\captionof{{table}}{{{0}}}\n'.format(caption)

            text += '\\end{center}\n'
        
        node = nodes.raw(text=text, format='latex', **self.options)
        node_list += [node]

        return node_list

rst.directives.register_directive('tbl', tbl_directive)

class problem_set_directive(rst.Directive):
    """
    -----------------------------------
    Docutils directive: ``problem-set``
    -----------------------------------

    Inserts a list of word problems.

    Example
    -------

    ::

        .. problem-set:: Homework for Week 1
            :solutions: hide
            :print-style: compact
            
            - cj8e28p004
            - cj8e28p007


        .. problem-set:: 
            :numbering: none

            [
                {
                    "question": "What is the speed of light?",
                    "answer": ":sci:`2.998E8` m/s",
                    "solution": "Ask Google__. \n\n__ http://www.google.com"
                },
                {
                    "question": "The Great Question of Life, the Universe, and Everything.",
                    "answer": "42",
                    "solution": "What do you get if you multiply six by nine?"
                }
            ]
    
    Options
    -------

        :numbering:   [*default*, none, bullets] + [0,1,2,3,...]
        :answers:     [*show*, toggle, hide]
        :solutions:   [show, *toggle*, hide]
        :print-style: [*simple*, compact, exam]

    Notes
    -----

    * Argument will be used as a subtitle.
    * Content required. 
    * Content may mix explicit problem dictionaries with slug references
    * Attempt to parse content as YAML then JSON. Malformed content will be returned.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'numbering'   : rst.directives.unchanged,
        'answers'     : rst.directives.unchanged,
        'solutions'   : rst.directives.unchanged,
        'print-style' : rst.directives.unchanged,
        }
    has_content = True

    def slug_lookup(self, slug):
        problem = {
            'slug': slug,
            'question': 'Slug-key ``{}`` not found.'.format(slug),
            'answer': '',
            'solution': '',
        }
        
        from apps.docmaker.models import ExerciseProblem
        try:
            obj = ExerciseProblem.objects.get(key=slug)
            problem = {
                'slug': slug,
                'admin_url': reverse('admin:docmaker_exerciseproblem_change', args=(obj.pk,)),
                'question': obj.question,
                'answer': obj.answer,
                'solution': obj.solution,
            }
        except:
            pass

        from apps.docmaker.models import ShortAnswerQuestion
        try:
            obj = ShortAnswerQuestion.objects.get(key=slug)
            problem = {
                'slug': slug,
                'admin_url': reverse('admin:docmaker_shortanswerquestion_change', args=(obj.pk,)),
                'question': obj.question,
                'answer': obj.answer,
                'solution': obj.solution,
            }
        except:
            pass
            
        return problem

    def unpack(self, problem, format):
    
        question = problem.get('question','').strip()
        answer = problem.get('answer','').strip()
        solution = problem.get('solution','').strip()

        if not question:
            question = ':highlight:`[ Question not available ]`'
        if not answer:
            answer = ':highlight:`[ Missing ]`'
        if not solution:
            solution = ':highlight:`[ No solution available ]`'
        
        if format == 'latex':
            writer = rst2latex
            kwargs = {}
        elif format == 'html':
            writer = rst2html
            kwargs = {'inline': True}
        else:
            writer = None
            kwargs = {}

        def write_part(part, writer=None, kwargs={}):
            if writer:
                if part[0] == '(': part = '\\' + part
                return writer(part, **kwargs)
            else:
                return part
            
        question = write_part(question, writer, kwargs)
        answer = write_part(answer, writer, kwargs)
        solution = write_part(solution, writer, kwargs)
            
        return question, answer, solution        
        
    def run(self):

        # Parse directive data

        self.assert_has_content()
        content = '\n'.join(self.content)#.replace('\\\\','\\')

        caption = ''
        if self.arguments: # use as caption
            caption = self.arguments[0]

        option_choices = ['default','none','bullets']
        numbering = self.options.get('numbering', option_choices[0])
        try:
            list_start = int(numbering)
        except:
            list_start = 1
            if numbering not in option_choices:
                numbering == option_choices[0]
            if numbering == 'none':
                numbering = ''
            
        option_choices = ['show','toggle','hide']
        answers = self.options.get('answers', option_choices[0])
        if answers not in option_choices:
            answers = option_choices[0]

        option_choices = ['toggle','hide','show']
        solutions = self.options.get('solutions', option_choices[0])
        if solutions not in option_choices:
            solutions = option_choices[0]

        option_choices = ['simple','compact','exam']
        print_style = self.options.get('print-style', option_choices[0])
        if print_style not in option_choices:
            print_style = option_choices[0]

        # Begin output
            
        node_list = []

        for load in [yaml.load, json.loads]:
            try:
                problem_set = load(content)
            except:
                problem_set = []
            if problem_set: break
                
        # Convert slugs to objects

        for index, obj in enumerate(problem_set):
            if isinstance(obj, basestring):
                slug = obj
            else:
                if 'question' in obj.keys():
                    slug = ''
                else:
                    slug = obj.get('slug','')
            if slug:
                problem_set[index] = self.slug_lookup(slug)
            
        # HTML writer specifics start...
        
        if problem_set:
            text = ''
            
            if caption:
                text += '<h4>{}</h4>\n'.format(rst2html(caption, inline=True))

            if numbering:
                if numbering == 'bullets':
                    text += '<ul class="docmaker inside-list">\n'
                else:
                    # ERROR: not sure why this markup does not seem to catch for list_start > 1 ...
                    text += '<ol start="{}" class="docmaker inside-list">\n'.format(list_start)

            n = list_start - 1
            for problem in problem_set:
                n += 1
                q, a, s = self.unpack(problem, format='html')
                toggle_id = '{:09}'.format(random.randrange(0,1e9))

                if numbering: 
                    text += '<li>\n'
                    
                if answers == 'toggle':
                    text += '<input class="toggler" type="button" rel="a{}" value="Show Answer" onclick="buttonToggle(this,\'Show Answer\',\'Hide Answer\')">\n'.format(toggle_id)
                if solutions == 'toggle':
                    text += '<input class="toggler" type="button" rel="s{}" value="Show Solution" onclick="buttonToggle(this,\'Show Solution\',\'Hide Solution\')">\n'.format(toggle_id)

                if 'admin_url' in problem:
                    text += '<p>{} <a class="for_staff" href="{}" target="_blank">{}</a></p>\n'.format(q, problem['admin_url'], problem['slug'])
                else:
                    text += '<p>{}</p>\n'.format(q)
                
                if answers == 'show':
                    text += '<div id="a{}" style="display:block">\n<i>Answer:</i> {}\n</div>\n'.format(toggle_id, a)
                elif answers == 'toggle':
                    text += '<div id="a{}" class="togglee">\n<i>Answer:</i> {}\n</div>\n'.format(toggle_id, a)

                if solutions == 'show':
                    text += '<div id="s{}" class="solution" style="display:block">\n<p>{}</p>\n</div>\n'.format(toggle_id, s)
                elif solutions == 'toggle':
                    text += '<div id="s{}" class="solution togglee">\n<p>{}</p>\n</div>\n'.format(toggle_id, s)
                    
                if numbering: 
                    text += '</li>\n'
                
            if numbering:
                if numbering == 'bullets':
                    text += '</ul>\n'
                else:
                    text += '</ol>\n'
        else:
            text = '<pre>Malformed input\n\n{}</pre>'.format(content)

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        # LaTeX writer specifics
        
        text = ''
        if problem_set:
            if caption:
                text += '\\subsubsection*{{{}}}\n\n'.format(rst2latex(caption))

            n = list_start - 1
            for problem in problem_set:
                n += 1
                q, a, s = self.unpack(problem, format='latex')
                
                if print_style == 'exam':
                    text += '\\parbox{\\textwidth}{'
                    text += '\\textbf{{{0}.}} \\quad {1}'.format(n, q)
                    text += '}'
                    text += '\\newpage'
                elif print_style == 'compact':
                    text += '\\addtolength\\textwidth{-\\adjwidth}'
                    text += '\\textbf{{{0}.}}\n'.format(n)
                    if answers in ['show','toggle']:
                        text += '\\marginpar{{\\footnotesize\\sf {0}}}\n'.format(a)
                    text += '\\quad \n{0}\n'.format(q)
                    if solutions in ['show','toggle']:
                        text += '\\par \\textbf{{Solution:}}\n\\par {0}\n'.format(s)
                    text += '\n'
                else: # print_style == 'simple'
                    text += '\\textbf{{{0}.}}\n'.format(n)
                    text += '\\quad \n{0}\n'.format(q)
                    if answers in ['show','toggle']:
                        text += '\\par \\textbf{{Answer:}} {0}\n'.format(a)
                    if solutions in ['show','toggle']:
                        text += '\\par \\textbf{{Solution:}}\n\\par {0}\n'.format(s)
                    text += '\n'
        else:
            text += '\\emph{Malformed input}\n'
            text += '\\begin{verbatim}\n'
            text += '{}\n'.format(content)
            text += '\\end{verbatim}\n'
            text += '\n'
        
        node = nodes.raw(text=text, format='latex', **self.options)
        node_list += [node]
        
        return node_list

rst.directives.register_directive('problem-set', problem_set_directive)

class equation_set_directive(rst.Directive):
    """
    -----------------------------------
    Docutils directive: ``equation-set``
    -----------------------------------

    Inserts a list of equations.

    Example
    -------

    ::

        .. equation-set:: Key Equations
            
            - name: Newton's second law
              latex: F = ma
    
    Options
    -------


    Notes
    -----

    * Argument will be used as a subtitle.
    * Content required. 
    * Content may mix explicit problem dictionaries with slug references
    * Attempt to parse content as YAML then JSON. Malformed content will be returned.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        }
    has_content = True

    def slug_lookup(self, slug):
        equation = {
            'name': 'Slug-key ``{}`` not found.'.format(slug),
            'latex': '',
        }
        
        from apps.docmaker.models import StudyEquation
        try:
            obj = StudyEquation.objects.get(key=slug)
            equation = {
                'name': obj.name,
                'latex': obj.latex,
            }
        except:
            pass

        equation['latex'] = '{{\\displaystyle {0}}}'.format(equation['latex'])
        return equation

    def run(self):

        # Parse directive data

        self.assert_has_content()
        content = '\n'.join(self.content)#.replace('\\\\','\\')

        caption = ''
        if self.arguments: # use as caption
            caption = self.arguments[0]

        # Begin output
            
        node_list = []

        for load in [yaml.load, json.loads]:
            try:
                equation_set = load(content)
            except:
                equation_set = []
            if equation_set: break
                
        # Convert slugs to objects

        for index, obj in enumerate(equation_set):
            if isinstance(obj, basestring):
                slug = obj
            else:
                if 'latex' in obj.keys():
                    slug = ''
                else:
                    slug = obj.get('slug','')
            if slug:
                equation_set[index] = self.slug_lookup(slug)
            
        # HTML writer specifics start...
        
        if equation_set:
            text = ''
            
            text += '\n<div class="equation-set">\n'
            if caption:
                text += '<h4>{}</h4>\n'.format(rst2html(caption, inline=True))

            text += '<dl>\n'
            for equation in equation_set:
                name = rst2html(equation['name'], inline=True)
                latex = rst2html('`{0}`'.format(equation['latex']), inline=True)
                text += '<dt>{0}</dt>\n'.format(name)
                text += '<dd>{0}</dd>\n'.format(latex)
            text += '</dl>\n'
            text += '</div>\n\n'
        else:
            text = '<pre>Malformed input\n\n{}</pre>'.format(content)

        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]

        # LaTeX writer specifics
        
        text = ''
        if equation_set:
            if caption:
                text += '\\subsubsection*{{{}}}\n\n'.format(rst2latex(caption))

            text += '\\begin{description}\n'
            for equation in equation_set:
                name = rst2latex(equation['name'])
                latex = equation['latex']
                text += '\\item[{0}] \\hfill \\\\ \n'.format(name)
                text += '$${0}$$\n'.format(latex)
            text += '\\end{description}\n'
        else:
            text += '\\emph{Malformed input}\n'
            text += '\\begin{verbatim}\n'
            text += '{}\n'.format(content)
            text += '\\end{verbatim}\n'
            text += '\n'
        
        node = nodes.raw(text=text, format='latex', **self.options)
        node_list += [node]
        
        return node_list

rst.directives.register_directive('equation-set', equation_set_directive)

class equipment_list_directive(rst.Directive):
    """
    -----------------------------------
    Docutils directive: ``equipment-list``
    -----------------------------------

    Inserts a list of word problems.

    Example
    -------

    ::

        .. equipment-list::
            :display: list
            
            - 6 scissors
            - graph-paper
            - 6 green-tape-rolls
            - 6 red-drinking-cups
            
            
        .. equipment-list::
            :display: table

            [
                {
                    "quantity": 6 ,
                    "item": "scissors",
                    "location": "E06"
                },
                {
                    "quantity": null,
                    "item": "graph paper",
                    "location": null
                }
            ]
            
    Options
    -------

        :display: [*list*, table]

    Notes
    -----

    * Any argument present will be ignored.
    * Content required. 
    * Content may mix explicit equipment request dictionaries with slug references.
    * Attempt to parsed content as YAML then JSON. Malformed content will be returned.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'display' : rst.directives.unchanged,
        }
    has_content = True

    def slug_lookup(self, slug):
        from apps.docmaker.models import LabEquipment
        try:
            # Does the lab equipment even have slugs ???
            obj = LabEquipment.objects.get(key=slug)
            item = obj.item
            location = obj.location
        except:
            item = ''
            location = ''
        return item, location

    def run(self):

        # Parse directive data

        option_choices = ['table','list']
        display = self.options.get('display', option_choices[0])
        if display not in option_choices:
            display = option_choices[0]

        content = '\n'.join(self.content)#.replace('\\\\','\\')

        # Construct output
            
        node_list = []

        for load in [yaml.load, json.loads]:
            try:
                equipment_list = load(content)
            except:
                equipment_list = []
            if equipment_list: break
                
        if equipment_list:

            # Convert slugs to objects

            if 'requests' in equipment_list:
                equipment_list = equipment_list['requests']

            for index, obj in enumerate(equipment_list):
                if isinstance(obj, basestring):
                    if ' ' in obj:
                        quantity, slug = obj.rsplit()
                    else:
                        quantity, slug = '', obj
                else:
                    quantity = obj.get('quantity','')
                    slug = obj.get('slug','')
                if slug:
                    item, location = self.slug_lookup(slug)
                    equipment_list[index] = {
                        'quantity': quantity,
                        'item': item,
                        'location': location,
                    }
            
            # Build HTML node
            
            text = ''
            
            if display == 'table':
                text += '<div class="my-docutils tbl equipment">\n'
                text += '<table>\n'
                text += '<tr>\n<th>Quantity</th>\n<th>Item</th>\n<th>Location</th>\n</tr>\n'
            else:
                text += '<ul>\n'

            for equipment in equipment_list:
                quantity = equipment.get('quantity','')
                item = rst2html(equipment.get('item',''),inline=True).title()
                location = rst2html(equipment.get('location',''),inline=True).title()

                if display == 'table':
                    if item:
                        if quantity:
                            text += '<tr>\n<td>{}</td>\n<td>{}</td>\n<td>{}</td>\n</tr>\n'.format(quantity, item, location)
                        else:
                            text += '<tr>\n<td></td>\n<td>{}</td>\n<td>{}</td>\n</tr>\n'.format(item, location)
                    else:
                        text += '<tr>\n<td colspan=3>&mdash;</td>\n</tr>\n'
                else:
                    text += '<li>{}</li>\n'.format(item)
                        
            if display == 'table':
                text += '</table>\n'
                text += '</div>\n'
            else:
                text += '</ul>\n'
                
            node = nodes.raw(text=text, format='html', **self.options)
            node_list += [node]     
        
            # Build LATEX node
            
            text = ''
            
            if display == 'table':
                text += '\\begin{center}\n'
                text += '\\begin{tabular}{|c|p{2.5in}|l|}\n'
                text += '\\hline\n'
                text += '\\makebox[1.0in]{\\textbf{Quantity}} &\n'
                text += '\\makebox[2.5in]{\\textbf{\\centering Items}} &\n'
                text += '\\makebox[1.0in]{\\textbf{Location}} \\\\\n'
                text += '\\hline\n'
            else:
                text += '\\begin{itemize}\n'

            for equipment in equipment_list:
                quantity = equipment.get('quantity','')
                item = rst2html(equipment.get('item',''),inline=True).title()
                location = rst2html(equipment.get('location',''),inline=True).title()

                if display == 'table':
                    text += '{} &\n'.format(quantity)
                    text += '{} &\n'.format(rst2latex(item))
                    text += '\\begin{minipage}{1.0in}\n'
                    text += '\\raggedright\n'
                    text += '\\vspace{1ex}\n'
                    text += '{} \\par'.format(rst2latex(location))
                    text += '\\vspace{1ex}\n'
                    text += '\\end{minipage}\n'
                    text += '\\\\\n'
                else:
                    text += '\\item {}\n'.format(item)
    
            if display == 'table':
                text += '\\hline\n'
                text += '\\end{tabular}\n'
                text += '\\end{center}\n\n'
            else:
                text += '\\end{itemize}\n\n'
                
            node = nodes.raw(text=text, format='latex', **self.options)
            node_list += [node]
            
        else:
            text = '<pre>Malformed input\n\n{}</pre>'.format(content)
            node = nodes.raw(text=text, format='html', **self.options)
            node_list += [node]     

        return node_list

rst.directives.register_directive('equipment-list', equipment_list_directive)
