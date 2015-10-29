from __future__ import division
from __future__ import unicode_literals

from docutils import nodes
from docutils.parsers import rst

def ref_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    ----------------------
    Docutils role: ``ref``
    ----------------------

    Inserts a hyperlink reference to a figure or table with a custom label.

    Example
    -------

   ::

        :ref:`image-filename.png`

    This will hyperlink to::

        .. fig:: Some image here
            :image: image-filename.png
            :scale: 0.75

    or

   ::

        :fig:`trapezoid`

    This will hyperlink to::

        .. fig:: Sample Trapezoid
            :position: side
            :label: trapezoid

            \begin{tikzpicture}
            \draw [fill=black!10] (-1,0.7) -- (1,0.7)
            -- (0.7,-0.7) -- (-0.7,-0.7) -- cycle;
            \end{tikzpicture}

    Notes
    -----

    * Works only for ``latex`` writer ... for now :)
    """

    ref = nodes.make_id(text)
    if role in ['fig', 'tbl']:
        ref = role + ':' + ref

    t = dict()

    t['latex'] = r'\hyperref[%s]{\ref*{%s}}' % (ref, ref)
    t['html']  = r'<a href="#%s">[link]</a>' % (ref,)

    node_list = [
        nodes.raw(text=t['latex'], format='latex'),
        nodes.raw(text=t['html'], format='html')
    ]

    return node_list, []

rst.roles.register_local_role('ref', ref_role)
rst.roles.register_local_role('fig', ref_role)
rst.roles.register_local_role('plt', ref_role)
rst.roles.register_local_role('tbl', ref_role)
rst.roles.register_local_role('eqn', ref_role) # don't forget to add tags to equations...

def jargon_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    -------------------------
    Docutils role: ``jargon``
    -------------------------

    Creates an index entry then bolds the term in the main text.

    Example
    -------

   ::

        We use a :jargon:`vector` to capture both direction and magnitude.
        An important tool in QED is the :jargon:`Feynman diagram`.
        :jargon:`~Energy` is the ability to do work.

    Notes
    -----

    * Force a conversion to lower case in the index with a tilde ``~``.  Useful
      when the term starts a sentence.
    * Works only for ``latex`` and ``html`` writers ...
    """

    t = dict()

    if text[0] == '~':
        text = text[1:]
        t['latex'] = r'\textbf{%s}\index{%s}' % (text,text.lower())
        t['html'] = '<strong>%s</strong>' % text
    else:
        t['latex'] = r'\textbf{%s}\index{%s}' % (text,text)
        t['html'] = '<strong>%s</strong>' % text

    node_list = [
        nodes.raw(text=t['latex'], format='latex'),
        nodes.raw(text=t['html'], format='html')
    ]

    return node_list, []

rst.roles.register_local_role('jargon', jargon_role)

def sci_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    ----------------------
    Docutils role: ``sci``
    ----------------------

    Displays scientific notation in the form :math:`a \times 10^{b}`.

    Example
    -------

   ::

        :sci:`4.5E+6`
        :sci:`450e-6`

    Notes
    -----

    * An abscissa of 1 is dropped: e.g., 1E10 => :math:`10^{10}`.
    * Upon error, the original text is returned.
    * Works only for ``latex`` and ``html`` writers ...
    """

    try:
        n = text.lower().split('e')
        a = float(n[0]) # just want to make sure it's a legit number
        a = n[0]        # make sure to take the abscissa as given
        b = int(n[1])   # must be an integer, this will drop the plus sign
        if a == '1':
            text = r'\(10^{%s}\)' % b
        else:
            text = r'\(%s \times 10^{%s}\)' % (a, b)
    except:
        pass

    node_list = [
        nodes.raw(text=text, format='latex'),
        nodes.raw(text=text, format='html'), # this pushes the work to MathJax
    ]

    return node_list, []

rst.roles.register_local_role('sci', sci_role)

def atm_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    ----------------------
    Docutils role: ``atm``
    ----------------------

    Displays pretty atomic symbols.

    Example
    -------

    ::

        :atm:`235:92:U`

    Notes
    -----

    * Upon error, the original text is returned.
    * Works only for ``latex`` and ``html`` writers ...
    """

    try:

        (a, z, sy) = text.split(':')
        dn = len(a) - len(z)
        if dn > 0:
            text = r'\({}^{%s}_{\phantom{%s}%s}\text{%s}\)' % (a, dn, z, sy)
        elif dn < 0:
            text = r'\({}^{\phantom{%s}%s}_{%s}\text{%s}\)' % (-dn, a, z, sy)
        else:
            text = r'\({}^{%s}_{%s}\text{%s}\)' % (a, z, sy)
    except:
        pass

    node_list = [
        nodes.raw(text=text, format='latex'),
        nodes.raw(text=text, format='html'), # this pushes the work to MathJax
    ]

    return node_list, []

rst.roles.register_local_role('atm', atm_role)

def highlight_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    """
    ----------------------------
    Docutils role: ``highlight``
    ----------------------------

    Highlights a span of text.
    """

    t = dict()

    t['latex'] = '\\underline{{{}}}'.format(text)
    t['html'] = '<span class="highlight">{}</span>'.format(text)

    node_list = [
        nodes.raw(text=t['latex'], format='latex'),
        nodes.raw(text=t['html'], format='html')
    ]

    return node_list, []

rst.roles.register_local_role('highlight', highlight_role)
