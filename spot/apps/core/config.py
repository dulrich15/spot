from __future__ import division
from __future__ import unicode_literals

import os
from django.conf import settings

page_path = os.path.join('..', '..', 'content', 'pages')
page_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), page_path)

if not os.path.exists(page_path):
    os.makedirs(page_path)

page_image_path = os.path.join(settings.MEDIA_ROOT, 'pages')

