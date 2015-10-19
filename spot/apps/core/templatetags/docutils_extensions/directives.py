from __future__ import division
from __future__ import unicode_literals

import codecs
import hashlib
import json
import os
import random
import re
import shutil
import yaml

from subprocess import Popen, PIPE
from PIL import Image

from docutils import nodes
from docutils.parsers import rst

from utils import rst2html
from utils import rst2latex
from utils import get_latex_path

from config import *

## -------------------------------------------------------------------------- ##

# class toggle_directive(rst.Directive):

    # required_arguments = 0
    # optional_arguments = 1
    # final_argument_whitespace = True
    # option_spec = {
        # 'access'     : rst.directives.unchanged,
    # }
    # has_content = True

    # def run(self):

        # self.assert_has_content()
        # content = '\n'.join(self.content).replace('\\\\','\\')

        # button_text = ''
        # if self.arguments:
            # button_text = self.arguments[0]

        # if 'access' in self.options.keys():
            # access = self.options['access']

        # text = ''
        # text += '<div class="docutils-extensions toggle">\n'
        # text += '<p><input class="toggler" type="button" value="{0}"></p>\n'.format(button_text)
        # text += '<div class="togglee" style="display:none">\n'
        # text += rst2html(content) + '\n'
        # text += '</div>\n'
        # text += '</div>\n'

        # node = nodes.raw(text=text, format='html', **self.options)
        # node_list = [node]

        # return node_list

## -------------------------------------------------------------------------- ##

class tbl_directive(rst.Directive):

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'label'     : rst.directives.unchanged,
        'cols'      : rst.directives.unchanged,
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

        text = ''
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

            divid = ''
            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
                divid = ' id="tbl:{0}"'.format(label)

            caption = ''
            if self.arguments: # use as caption
                caption = rst2html(self.arguments[0], inline=True)

            colspec = len(tbl[0]) * 'c'
            if 'cols' in self.options.keys():
                colspec = self.options['cols']
            align = {'l': 'left', 'c': 'center', 'r': 'right'}

            text = ''
            text += '<div{} class="docutils-extensions tbl">\n'.format(divid)
            text += '<table>\n'

            for tag, rows in [('th', tbl[1]), ('td', tbl[2])]:
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
                            cellalign = align[colspec[row.index(cell)]]
                            celltext = rst2html('\n'.join(cell[3]), inline=True)

                            text += '<{}{}{} style="text-align:{}">\n'.format(
                                tag, rowspan, colspan, cellalign)
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
                colspec = self.options['cols']
        
            text += '\\renewcommand{\\arraystretch}{1.5}\n'
            text += '\\renewcommand{\\tabcolsep}{0.2cm}\n'
            text += '\\begin{center}\n'

            if label:
                text += '\\label{{tbl:{0}}}\n'.format(label)
                
            text += '\\begin{{tabular}}{{{0}}}\n'.format(colspec)
            text += '\\hline\n'
            if headrows:
                for row in headrows:
                    celltext = []
                    for cell in row:
                        if cell:
                            celltext += [rst2latex('\n'.join(cell[3]))]
                        else:
                            celltext += ['']
                    text += ' & '.join(celltext) + ' \\\\\n'
                text += '\\hline\n'
            for row in bodyrows:
                celltext = []
                for cell in row:
                    if cell:
                        celltext.append(rst2latex('\n'.join(cell[3])))
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
## -------------------------------------------------------------------------- ##

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

class fig_directive(rst.Directive):

    """
    ---------------------------
    Docutils directive: ``fig``
    ---------------------------

    Inserts a figure. Creates it if necessary.

    Example
    -------

    ::

        .. fig:: Some image here
            :image: image-filename.png
            :scale: 0.75

        .. fig:: Sample Trapezoid
            :label: trapezoid

            \begin{tikzpicture}
            \draw [fill=black!10] (-1,0.7) -- (1,0.7)
            -- (0.7,-0.7) -- (-0.7,-0.7) -- cycle;
            \end{tikzpicture}

        .. fig:: Some numbers
            :template: matplotlib-pyplot

            plt.plot([1,2,3,4], [1,4,9,16], 'ro')
            plt.axis([0, 6, 0, 20])
            plt.ylabel('some numbers')
            
    Options
    -------

    :image:     Used to insert images. Any content will be ignored. A label
                will be inserted with the image's filename.
    :scale:     Used to scale the image.
    :label:     Used for hyperlinks references. See ``fig`` role.
    :template:  Used to point to proper templale when creating image. Default 
                is ``latex-preview``.

    Notes
    -----

    * Argument used for figure caption (optional).
    * If image option is used, label defaults to image name.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'image'     : rst.directives.unchanged,
        'scale'     : rst.directives.unchanged,
        'label'     : rst.directives.unchanged,
        'template'  : rst.directives.unchanged,
    }
    has_content = True

    def run(self):

        node_list = []

        text = ''
        
        try:
            scale = float(self.options['scale'])
        except:
            scale = 1.00

        if 'image' in self.options:
            image_name = self.options['image']
            
            if '://' in image_name:
                image_path = ''
                image_url = image_name
            else:
                image_path = os.path.join(WIKI_IMAGE_PATH, image_name)
                image_url = '/'.join([WIKI_IMAGE_URL, image_name])

                if not os.path.exists(image_path):
                    print '* ERROR: Missing: ' + image_path
                    text += '<p class="warning">'
                    text += 'Missing image : {}'.format(image_name)
                    text += '</p>\n'.format(image_name)
        else:
            # Unlike a normal image, our reference will come from the content...
            self.assert_has_content()
            content = '\n'.join(self.content).replace('\\\\','\\')
            image_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

            if 'template' in self.options:
                type, template = self.options['template'].split('-')
            else:
                type = 'latex'
                template = 'preview'

            if template == 'animation':
                image_name = '{}.mp4'.format(image_hash)
            else:
                image_name = '{}.png'.format(image_hash)

            image_path = os.path.join(WIKI_IMAGE_PATH, SYSGEN_FOLDER, image_name)
            image_url = '/'.join([WIKI_IMAGE_URL, SYSGEN_FOLDER, image_name])
                
            if not os.path.exists(image_path):
                self.build_image(image_path, content, type, template)

            if not os.path.exists(image_path):
                print '* ERROR: Missing: ' + image_path
                text += '<div class="warning">\n'
                text += '<h4>File generation error:</h4>\n'
                text += '<pre><code>'
                text += '\n'.join(self.content) + '\n'
                text += '</code></pre>\n'
                text += '</div>\n\n'
                
        if not text:
            if 'label' in self.options.keys():
                label = nodes.make_id(self.options['label'])
            else:
                label = nodes.make_id(image_name)

            text += '<div id="fig:{0}" class="docutils-extensions fig">\n'.format(label)

            text += '<a href="{0}">\n'.format(image_url)
            try:
                if image_path:
                    i = Image.open(image_path)
                    x = int(scale * i.size[0])
                    y = int(scale * i.size[1])
                    text += '<img width="{1}px" height="{2}"px src="{0}">\n'.format(image_url, x, y)
                else:
                    text += '<img src="{0}">\n'.format(image_url)
            except:
                ext = os.path.basename(image_path).rsplit('.')[1]
                if ext == 'mp4':
                    cmd = [FFMPEG_CMD, '-i', image_path]
                    p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                    out, err = p.communicate()
                    
                    m = re.search(r'Stream.*Video.*, (\d+)x(\d+)', err)
                    if m:
                        x = int(scale * float(m.group(1)))
                        y = int(scale * float(m.group(2)))
                        text += '<video width="{1}px" height="{2}px" controls><source src="{0}" type="video/mp4"></video>\n'.format(image_url, x, y)
                    else:
                        text += '<video controls><source src="{0}" type="video/mp4"></video>\n'.format(image_url)
            text += '</a>\n'            

            if self.arguments:
                text += rst2html(self.arguments[0])

            text += '</div>\n'            
            
        node = nodes.raw(text=text, format='html', **self.options)
        node_list += [node]




        
# LaTeX writer specifics start (offset is ignored for HTML writer)

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

                if not os.path.exists(image_path):
                    print 'Could not locate "%s"' % image_path

                latex_path = get_latex_path(image_path)

                figtext = r'\includegraphics[scale=%s]{%s}'
                figtext = figtext % (scale, latex_path)
                if not label:
                    label = nodes.make_id(image)
                    label = r'\label{fig:%s}' % label
            else:
                figtext = image
        else:
# Note the `everymath` statement below. This switches the default behavior of 
# inline math to display style. For *figures* I am constantly enforcing display
# mode, so this seems like a better default for my purpose. Use `textstyle` to 
# get the regular behavior, e.g., "\textstyle \int x dx = \frac{1}{2} x^2"
            figtext = '\n\\everymath{\\displaystyle}\n'
            figtext += '\n'.join(self.content)
            figtext += '\n\\everymath{\\textstyle}\n'

        text = FIG_TEMPLATE['default'] % {
            'caption'   : caption,
            'label'     : label,
            'figtext'   : figtext,
            }

        node = nodes.raw(text=text, format='latex', **self.options)
        node_list += [node]
        
        
        
        
        
        return node_list
        
    def build_image(self, image_path, content, type, template):
        print '* Trying to build {}'.format(image_path)

        ext = os.path.basename(image_path).split('.')[1]
        tempfile = '.'.join(['temp', ext])
        
        # try:
        if 1==1:
            # Let's remember where we came from...
            curdir = os.getcwd()
            newdir = os.path.join(WORK_PATH, type, '_')
            template_dir = os.path.normpath(os.path.join(newdir, '..'))

            # Move to proper working directory for this type of content
            os.chdir(newdir)
            print '* Moved to work directory at {}'.format(newdir)
            if os.path.isfile(tempfile):
                os.remove(tempfile)
                
            print '* Construction template = {}-{}'.format(type, template)
            if type == 'latex':
            
                # Load template to memory
                template += '.tex'
                template_path = os.path.join(template_dir, template)
                f = codecs.open(template_path, 'r', 'utf-8')
                template = f.read()
                f.close()
                print '* Template found at {}'.format(template_path)
                
                # Write the LaTeX file to the working folder
                f = codecs.open('temp.tex', 'w', 'utf-8')
                f.write(template % content)
                f.close()

                print '* Running LaTeX (temp.tex --> temp.pdf)'
                cmd = os.path.join(LATEX_PATH, 'pdflatex')
                cmd = [cmd, '--interaction=nonstopmode', 'temp.tex']
                p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                out, err = p.communicate()

                print '* Running LaTeX (temp.tex --> temp.pdf)'
                cmd = os.path.join(LATEX_PATH, 'pdflatex')
                cmd = [cmd, '--interaction=nonstopmode', 'temp.tex']
                p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                out, err = p.communicate()

                print '* Running Ghostscript (temp.pdf --> temp.png)'
                cmd = [GS_COMMAND,
                '-q',
                '-dBATCH',
                '-dNOPAUSE',
                '-sDEVICE=png16m',
                '-r600', # this number should be changed with img_scale below
                '-dTextAlphaBits=4',
                '-dGraphicsAlphaBits=4',
                '-sOutputFile=temp.png',
                'temp.pdf',
                ]
                p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                out, err = p.communicate()
                
                img_scale = 0.20 # not sure why, but this just "looks right"
                
            elif type == 'matplotlib':
                
                # Have to have some serious protection here....
                if '\nimport' in content:
                    assert False
                    
                # Load template to memory
                template += '.py'
                template_path = os.path.join(template_dir, template)
                f = codecs.open(template_path, 'r', 'utf-8')
                template = f.read()
                f.close()
                print '* Template found at {}'.format(template_path)

                # Write the matplotlib file to the working folder
                f = codecs.open('temp.py', 'w', 'utf-8')
                f.write(template % content)
                f.close()
                
                # Run matplotlib ...
                cmd = [PYTHON_CMD, 'temp.py']
                p = Popen(cmd,stdout=PIPE,stderr=PIPE)
                out, err = p.communicate()

                img_scale = 0.70 # not sure why, but this just "looks right"
                
            else:
            
                type = None
                img_scale = 1.00

            if type: # then capture the file we just built            

                if ext == 'png':
                    print '* Resizing {}'.format(tempfile)
                    img = Image.open(tempfile)
                    x = int(img_scale * img.size[0])
                    y = int(img_scale * img.size[1])
                    img = img.resize((x, y), Image.ANTIALIAS)
                    img.save(tempfile, 'png')

                # Is the output folder even there?
                d = os.path.dirname(image_path)
                if not os.path.exists(d):
                    os.makedirs(d)

                # Finally, move the image file and clean up
                if os.path.exists(tempfile):
                    shutil.copyfile(tempfile, image_path)
                    os.remove(tempfile)

                print '* New file saved at {}'.format(image_path)
                os.chdir(curdir)
                
        # except:
            # pass

        return image_path
        
## -------------------------------------------------------------------------- ##

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
            :numbering: none
            :solutions: hide

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
        :print-style: [*compact*, simple]

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

    def unpack(self, problem, format):
    
        question = problem.get('question','')
        answer = problem.get('answer','')
        solution = problem.get('solution','')

        if not question:
            question = ':highlight:`Question not available`'
        if not answer:
            answer = ':highlight:`Missing`'
        if not solution:
            solution = ':highlight:`No solution available`'
        
        if format == 'html':
            writer = rst2html
            kwargs = {'inline': True}
        elif format == 'latex':
            writer = rst2latex
            kwargs = {}
        else:
            writer = None
            kwargs = {}

        def write_part(part, writer=None, kwargs={}):
            if writer:
                part = part.strip()
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
        content = '\n'.join(self.content) # .replace('\\\\','\\')

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

        option_choices = ['simple','compact']
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
                
        # HTML writer specifics start...
        
        if problem_set:
            text = ''
            
            if caption:
                text += '<h4>{}</h4>\n'.format(rst2html(caption, inline=True))

            if numbering:
                if numbering == 'bullets':
                    text += '<ul class="inside-list">\n'
                else:
                    # ERROR: not sure why this markup does not seem to catch for list_start > 1 ...
                    text += '<ol start="{:02}" class="inside-list">\n'.format(list_start)

            n = list_start - 1
            for problem in problem_set:
                n += 1
                q, a, s = self.unpack(problem, format='html')
                toggle_id = '{:09}'.format(random.randrange(0,1e9))

                if numbering: 
                    text += '<li>\n'
                    
                if answers == 'toggle':
                    text += '<input class="toggler" type="button" rel="a{}" value="Show Answer" onclick="buttonToggle(this,\'Show Answer\',\'Hide Answer\')">\n'.format(toggle_id)

                text += '<p>{}</p>\n'.format(q)

                if answers == 'show':
                    text += '<p id="a{}">\n'.format(toggle_id)
                    if solutions == 'toggle':
                        text += '<input class="toggler" type="button" rel="s{}" value="Show Solution" onclick="buttonToggle(this,\'Show Solution\',\'Hide Solution\')">\n'.format(toggle_id)
                    text += '<i>Answer:</i> {}\n'.format(a)
                    text += '</p>\n'
                elif answers == 'toggle':
                    text += '<div id="a{}" class="togglee">\n'.format(toggle_id)
                    if solutions == 'toggle':
                        text += '<input class="toggler" type="button" rel="s{}" value="Show Solution" onclick="buttonToggle(this,\'Show Solution\',\'Hide Solution\')">\n'.format(toggle_id)
                    text += '<i>Answer:</i> {}\n'.format(a)
                    text += '</div>\n'

                if solutions == 'show':
                    text += '<div id="s{}" class="solution" style="display:block">\n'.format(toggle_id)
                    text += '<p>{}</p>\n'.format(s)
                    text += '</div>\n'
                elif solutions == 'toggle':
                    text += '<div id="s{}" class="solution togglee">\n'.format(toggle_id)
                    text += '<p>{}</p>\n'.format(s)
                    text += '</div>\n'
                    
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
                
                if print_style == 'simple':
                    text += '\\textbf{{{0}.}}\n'.format(n)
                    text += '\\quad \n{0}\n'.format(q)
                    if answers in ['show','toggle']:
                        text += '\\par \\textbf{{Answer:}} {0}\n'.format(a)
                    if solutions in ['show','toggle']:
                        text += '\\par \\textbf{{Solution:}}\n\\par {0}\n'.format(s)
                    text += '\n'
                else:
                    text += '\\addtolength\\textwidth{-\\adjwidth}'
                    text += '\\textbf{{{0}.}}\n'.format(n)
                    if answers in ['show','toggle']:
                        text += '\\marginpar{{\\footnotesize\\sf {0}}}\n'.format(a)
                    text += '\\quad \n{0}\n'.format(q)
                    if answers in ['show','toggle'] and solutions in ['show','toggle']:
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
