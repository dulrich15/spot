from __future__ import division
from __future__ import unicode_literals

import os
import fnmatch

def get_choices_from_path(mypath, filter='*'):
    choices = []
    for dirpath, dirnames, filenames in os.walk(mypath):
        for f in sorted(filenames):
            filepath = os.path.join(dirpath, f)
            filename = filepath.replace(mypath, '')[1:]
            filename = '/'.join(filename.split(os.path.sep))
            if fnmatch.fnmatch(filename, filter):
                choices += [(filename, filename)]
    return choices
