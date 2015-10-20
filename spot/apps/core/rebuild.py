from __future__ import division
from __future__ import unicode_literals

import os
import shutil
import sys

from models import Page
from config import page_path
from templatetags.docutils_extensions.config import SYSGEN_FOLDER

def rebuild(wipe_sysgen=False):
    '''
    Designed to be run from shell. 
    Will wipe DB and load data from file system.
    '''
    url_list = []
    for root, dirs, files in os.walk(page_path):
        head = root.replace(page_path, '')
        path = head.split(os.sep)
        for file in files:
            url = '/'.join(path + [file])
            if url[-1:] == '_':
                url = url[:-1]
            else:
                url = url + '/'
            print url
            url_list.append(url)

    confirm = raw_input('About to create {} pages. Ready to wipe DB ([y]/n)? '.format(len(url_list)))
    if confirm and confirm.upper() != 'Y':
        print 'Aborting...'
        sys.exit()
        
    print 'Deleting all Page data'
    Page.objects.all().delete()

    if wipe_sysgen:
        print 'Wiping sysgen'
        for file in os.listdir(SYSGEN_FOLDER):
            file_path = os.path.join(SYSGEN_FOLDER, file)
            if os.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.unlink(file_path)

    for url in sorted(url_list):
        print 'Creating: ', url
        page = Page(url=url)
        page.update()
