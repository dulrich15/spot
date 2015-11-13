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

        :atm:`U-235`

    Notes
    -----

    * Upon error, the original text is returned.
    * Works only for ``latex`` and ``html`` writers ...
    """

    atomic_numbers = {
        'H'  :   1, # Hydrogen
        'He' :   2, # Helium
        'Li' :   3, # Lithium
        'Be' :   4, # Beryllium
        'B'  :   5, # Boron
        'C'  :   6, # Carbon
        'N'  :   7, # Nitrogen
        'O'  :   8, # Oxygen
        'F'  :   9, # Fluorine
        'Ne' :  10, # Neon
        'Na' :  11, # Sodium
        'Mg' :  12, # Magnesium
        'Al' :  13, # Aluminium
        'Si' :  14, # Silicon
        'P'  :  15, # Phosphorus
        'S'  :  16, # Sulfur
        'Cl' :  17, # Chlorine
        'Ar' :  18, # Argon
        'K'  :  19, # Potassium
        'Ca' :  20, # Calcium
        'Sc' :  21, # Scandium
        'Ti' :  22, # Titanium
        'V'  :  23, # Vanadium
        'Cr' :  24, # Chromium
        'Mn' :  25, # Manganese
        'Fe' :  26, # Iron
        'Co' :  27, # Cobalt
        'Ni' :  28, # Nickel
        'Cu' :  29, # Copper
        'Zn' :  30, # Zinc
        'Ga' :  31, # Gallium
        'Ge' :  32, # Germanium
        'As' :  33, # Arsenic
        'Se' :  34, # Selenium
        'Br' :  35, # Bromine
        'Kr' :  36, # Krypton
        'Rb' :  37, # Rubidium
        'Sr' :  38, # Strontium
        'Y'  :  39, # Yttrium
        'Zr' :  40, # Zirconium
        'Nb' :  41, # Niobium
        'Mo' :  42, # Molybdenum
        'Tc' :  43, # Technetium
        'Ru' :  44, # Ruthenium
        'Rh' :  45, # Rhodium
        'Pd' :  46, # Palladium
        'Ag' :  47, # Silver
        'Cd' :  48, # Cadmium
        'In' :  49, # Indium
        'Sn' :  50, # Tin
        'Sb' :  51, # Antimony
        'Te' :  52, # Tellurium
        'I'  :  53, # Iodine
        'Xe' :  54, # Xenon
        'Cs' :  55, # Cesium
        'Ba' :  56, # Barium
        'La' :  57, # Lanthanum
        'Ce' :  58, # Cerium
        'Pr' :  59, # Praseodymium
        'Nd' :  60, # Neodymium
        'Pm' :  61, # Promethium
        'Sm' :  62, # Samarium
        'Eu' :  63, # Europium
        'Gd' :  64, # Gadolinium
        'Tb' :  65, # Terbium
        'Dy' :  66, # Dysprosium
        'Ho' :  67, # Holmium
        'Er' :  68, # Erbium
        'Tm' :  69, # Thulium
        'Yb' :  70, # Ytterbium
        'Lu' :  71, # Lutetium
        'Hf' :  72, # Hafnium
        'Ta' :  73, # Tantalum
        'W'  :  74, # Tungsten
        'Re' :  75, # Rhenium
        'Os' :  76, # Osmium
        'Ir' :  77, # Iridium
        'Pt' :  78, # Platinum
        'Au' :  79, # Gold
        'Hg' :  80, # Mercury
        'Tl' :  81, # Thallium
        'Pb' :  82, # Lead
        'Bi' :  83, # Bismuth
        'Po' :  84, # Polonium
        'At' :  85, # Astatine
        'Rn' :  86, # Radon
        'Fr' :  87, # Francium
        'Ra' :  88, # Radium
        'Ac' :  89, # Actinium
        'Th' :  90, # Thorium
        'Pa' :  91, # Protactinium
        'U'  :  92, # Uranium
        'Np' :  93, # Neptunium
        'Pu' :  94, # Plutonium
        'Am' :  95, # Americium
        'Cm' :  96, # Curium
        'Bk' :  97, # Berkelium
        'Cf' :  98, # Californium
        'Es' :  99, # Einsteinium
        'Fm' : 100, # Fermium
        'Md' : 101, # Mendelevium
        'No' : 102, # Nobelium
        'Lr' : 103, # Lawrencium
        'Rf' : 104, # Rutherfordium
        'Db' : 105, # Dubnium
        'Sg' : 106, # Seaborgium
        'Bh' : 107, # Bohrium
        'Hs' : 108, # Hassium
        'Mt' : 109, # Meitnerium
        'Ds' : 110, # Darmstadtium
        'Rg' : 111, # Roentgenium
        'Cn' : 112, # Copernicium
        'Uut': 113, # Ununtrium
        'Fl' : 114, # Flerovium
        'Uup': 115, # Ununpentium
        'Lv' : 116, # Livermorium
        'Uus': 117, # Ununseptium
        'Uuo': 118, # Ununoctium
    }
    specials = {
        'neutron'   : ('n', 1, 0),
        'proton'    : ('p', 1, 1),
        'electron'  : ('e', 0, -1),
    }

    try:
        if text in specials:
            symbol, a, z = specials[text]
        else:
            symbol, nbr = text.split('-')
            a = int(nbr)
            z = atomic_numbers[symbol.title()]

        offset = len(str(a)) - len(str(z))
        if offset > 0:
            text = r'\({}^{%s}_{\phantom{%s}%s}\text{%s}\)' % (a, offset, z, symbol)
        elif offset < 0:
            text = r'\({}^{\phantom{%s}%s}_{%s}\text{%s}\)' % (-offset, a, z, symbol)
        else:
            text = r'\({}^{%s}_{%s}\text{%s}\)' % (a, z, symbol)
    except:

        try: # backward-compatible format :atm:`235:92:U`
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
