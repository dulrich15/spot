from __future__ import division
from __future__ import unicode_literals

import os

from django.conf import settings

# System-specific commands/locations
LATEX_PATH = ''
GS_COMMAND = 'gs'
PYTHON_CMD = 'python'
FFMPEG_CMD = 'ffmpeg'

# Directory within docutils_extensions to find working folders
WORK_PATH = ''
WORK_PATH = os.path.join(os.path.dirname(os.path.abspath( __file__ )), WORK_PATH)

# Directory within MEDIA_ROOT where wiki images are
WIKI_IMAGE_FOLDER = 'wiki'
WIKI_IMAGE_PATH = os.path.join(settings.MEDIA_ROOT, WIKI_IMAGE_FOLDER)
WIKI_IMAGE_URL = '/'.join([settings.MEDIA_URL, WIKI_IMAGE_FOLDER])

# Directory within WIKI_IMAGE_FOLDER where system-generated images will go
SYSGEN_FOLDER = 'sysgen'
