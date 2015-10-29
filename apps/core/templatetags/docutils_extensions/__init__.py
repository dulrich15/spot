from docutils.parsers import rst

from roles import *
from directives import *

rst.roles.register_local_role('sci', sci_role)
rst.roles.register_local_role('atm', atm_role)
rst.roles.register_local_role('jargon', jargon_role)
rst.roles.register_local_role('highlight', highlight_role)

# rst.roles.register_local_role('ref', ref_role)
# rst.roles.register_local_role('eqn', ref_role)
# rst.roles.register_local_role('tbl', ref_role)
# rst.roles.register_local_role('fig', ref_role)
# rst.roles.register_local_role('plt', ref_role)
# rst.roles.register_local_role('ani', ref_role)

# rst.directives.register_directive('toggle', toggle_directive)

rst.directives.register_directive('tbl', tbl_directive)
rst.directives.register_directive('fig', fig_directive)
# rst.directives.register_directive('plt', plt_directive)
# rst.directives.register_directive('ani', plt_directive)

rst.directives.register_directive('problem-set', problem_set_directive)
