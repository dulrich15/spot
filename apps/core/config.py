from __future__ import division
from __future__ import unicode_literals

import os
import posixpath

from django.conf import settings

# Location of special content files
CONTENT_PATH = os.path.join(settings.BASE_DIR, 'content')

# Location to store text file versions of Pages data
PAGE_PATH = os.path.join(CONTENT_PATH, 'pages')

if not os.path.exists(PAGE_PATH):
    os.makedirs(PAGE_PATH)

# Location of images for pages
IMAGE_URL = posixpath.join(settings.STATIC_URL, 'images')
IMAGE_PATH = os.path.join(CONTENT_PATH, 'images')

if not os.path.exists(IMAGE_PATH):
    os.makedirs(IMAGE_PATH)

# Where we keep the banners
BANNER_URL = posixpath.join(IMAGE_URL, 'banners')
BANNER_PATH = os.path.join(IMAGE_PATH, 'banners')

if not os.path.exists(IMAGE_PATH):
    os.makedirs(IMAGE_PATH)

# Directory within IMAGE_FOLDER where system-generated images will go
SYSGEN_URL = posixpath.join(IMAGE_URL, 'sysgen')
SYSGEN_PATH = os.path.join(IMAGE_PATH, 'sysgen')

if not os.path.exists(SYSGEN_PATH):
    os.makedirs(SYSGEN_PATH)

# System-specific commands/locations
LATEX_CMD  = ''
GS_CMD     = 'gs'
PYTHON_CMD = 'python'
FFMPEG_CMD = 'ffmpeg'
