from __future__ import division
from __future__ import unicode_literals

import codecs
import copy
import datetime
import fnmatch
import os
import posixpath
import re

from django.core.urlresolvers import reverse
from django.db.models import *

from config import BANNER_PATH
from config import BANNER_URL
from config import PAGE_PATH

from templatetags.docutils_extensions.writers import rst2xml

from utils import get_choices_from_path

class Classroom(Model):
    slug = SlugField(max_length=64,unique=True)
    title = CharField(max_length=256,blank=True,editable=False)
    subtitle = CharField(max_length=256,blank=True,editable=False)
    instructor = CharField(max_length=256,blank=True,editable=False)
    first_date = DateField(null=True,blank=True,editable=False)
    
    banner_filename = CharField(max_length=200,choices=get_choices_from_path(BANNER_PATH),null=True,blank=True)
    home_page = ForeignKey('Page',editable=False)

    @property
    def is_active(self):
        return ( self.home_page.restriction_level < 2 )
        
    @property
    def url(self):
        return '/{}/'.format(self.slug)
        
    @property
    def banner(self):
        banner = dict()
        banner['filename'] = self.banner_filename
        banner['filepath'] = os.path.join(BANNER_PATH, banner['filename'])
        banner['exists'] = os.path.isfile(banner['filepath'])
        banner['url'] = posixpath.join(BANNER_URL, banner['filename'])
        return banner

    def banner_link(self):
        return '<a class="imagelink" href="{url}"><img src="{url}"></a>'.format(url=self.banner['url'])
    banner_link.allow_tags = True

    def banner_thumbnail(self):
        return '<a class="thumbnail" href="{url}"><img src="{url}"></a>'.format(url=self.banner['url'])
    banner_thumbnail.allow_tags = True

    def save(self, args=[], kwargs={}):
        try:
            home_page = Page.objects.get(url=self.url)
        except:
            home_page = Page(url=self.url)
            home_page.save()
        
        self.home_page = home_page
        self.title = home_page.title or self.slug
        self.subtitle = home_page.subtitle
        self.instructor = home_page.author
        self.first_date = home_page.date
        
        super(Classroom, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.slug
        
    class Meta:
        ordering = ['slug']


print_template_choices = [
    ('print_page.tex','Page'),
    ('print_book.tex','Book'),
    ('print_exam.tex','Exam'),
    ('print_equipment_form.tex','Equipment'),
]
access_level_choices = [
    (0,'Public'),
    (1,'Student'),
    (2,'Instructor'),
]

class Page(Model):
    url = CharField(max_length=1024,unique=True)
    parent = ForeignKey('Page',null=True,blank=True,editable=False)

    raw_content = TextField(blank=True)

    title = CharField(max_length=256,blank=True,editable=False)
    subtitle = CharField(max_length=256,blank=True,editable=False)
    author = CharField(max_length=256,blank=True,editable=False)
    date = DateField(null=True,blank=True,editable=False)

    print_template = CharField(max_length=256,default=print_template_choices[0][0],choices=print_template_choices,editable=False)
    access_level = PositiveSmallIntegerField(default=access_level_choices[0][0],choices=access_level_choices,editable=False)

    create_date = DateTimeField(auto_now_add=True)
    last_update = DateTimeField(auto_now=True)

    @property
    def content(self):
        content = self.raw_content

        def repl(match):
            page_url = match.group(1)
            try:
                page = Page.objects.get(url=page_url)
                root_url = reverse('show_page', args=['/'])
                link_url = os.path.abspath(os.path.join(root_url, page_url[1:]))
                docutils_link_text = r'`{} <{}/>`_'.format(page.title, link_url)
            except:
                docutils_link_text = r'<<{}>>'.format(page_url)
            return docutils_link_text
        
        pattern = r'<<(/[^\s]+/)>>'
        content = re.sub(pattern, repl, content)

        return content

    @property
    def classroom(self):
        try:
            slug = self.url.split('/')[1]
            classroom = Classroom.objects.get(slug=slug)
        except:
            classroom = None
        return classroom

    @property
    def children(self):
        return Page.objects.filter(parent=self)
        
    @property
    def siblings(self):
        return Page.objects.filter(parent=self.parent).exclude(pk=self.pk)
        
    @property
    def filepath(self):
        filepath = os.path.abspath(os.path.join(PAGE_PATH, self.url[1:]))
        if os.path.isdir(filepath):
            filepath = os.path.abspath(os.path.join(PAGE_PATH, self.url[1:], '_'))
        return filepath
        
    @property
    def restriction_level(self):
        if not self.parent:
            restriction_level = 2
        else:
            restriction_level = self.access_level
            if self.parent.parent:
                if self.parent.restriction_level > restriction_level:
                    restriction_level = self.parent.restriction_level
        return restriction_level
        
    def update(self, force_update=False): # check file system for updated version
        fp = self.filepath
        if os.path.isfile(fp):
            should_update = True
            if self.last_update:
                mod_timestamp = os.path.getmtime(fp)
                mod_datetime = datetime.datetime.fromtimestamp(mod_timestamp)
                if mod_datetime < self.last_update:
                    should_update = False
            if should_update or force_update:
                f = codecs.open(fp, 'r+', 'utf-8')
                content = f.read()
                f.close()
                self.raw_content = content
        self.save()
        
    def save(self, args=[], kwargs={}):
        x = rst2xml(self.content)
        
        title = x.find('title')
        subtitle = x.find('subtitle')
        author = None
        date = None
        access_level = None
        print_template = None
        
        docinfo = x.find('docinfo')
        if docinfo is not None:
            author = docinfo.find('author')
            date = docinfo.find('date')
            if docinfo.findall('field'):
                for f in docinfo.findall('field'):
                    field_name = f.find('field_name').text
                    field_body = f.find('field_body').find('paragraph')
                    if field_name.lower() == 'title':
                        title = field_body
                    if field_name.lower() == 'subtitle':
                        subtitle = field_body
                    if field_name.lower() == 'instructor':
                        author = field_body
                    if field_name.lower() == 'first-day':
                        date = field_body
                    if field_name.lower() == 'access-level':
                        access_level = field_body
                    if field_name.lower() == 'print-template':
                        print_template = field_body

        self.title = self.url
        if title is not None:
            self.title = title.text

        self.subtitle = ''
        if subtitle is not None:
            self.subtitle = subtitle.text

        self.access_level = access_level_choices[0][0]
        if access_level is not None:
            for (value, key) in access_level_choices:
                if access_level.text == key.lower():
                    self.access_level = value
                    break
            
        self.print_template = print_template_choices[0][0]
        if print_template is not None:
            for (value, key) in print_template_choices:
                if print_template.text == key.lower():
                    self.print_template = value
                    break
            
        self.author = ''
        if author is not None:
            self.author = author.text

        self.date = None
        if date is not None:
            try:
                self.date = datetime.datetime.strptime(date.text, '%Y-%m-%d')
            except:
                pass
            
        self.parent = None            
        if self.url != '/':
            parent_url = self.url.rsplit('/',2)[0] + '/'

            try:
                self.parent = Page.objects.get(url=parent_url)
            except:
                self.parent = Page(url=parent_url)
                self.parent.save()
                
            try:
                classroom = Classroom.objects.get(home_page=self)
                classroom.save()
            except:
                pass

        # save a copy to the file system

        fp = self.filepath
        if not os.path.isfile(fp): # then will have to do something unusual
            if os.path.isdir(fp): # then save the content in a special file
                fp = fp + '/_'
            else: # the page doesn't exist --- before we build it, we need to
                  # make sure the directory structure is compatible
                dirs = self.url.split('/')
                fp = PAGE_PATH
                for d in dirs[:-1]: # these directories should all exist
                    fp = os.path.join(fp, d)
                    if os.path.isfile(fp): # then we need to prepare to push this content into a new directory
                        os.rename(fp, fp + '__')
                    if not os.path.isdir(fp): # then we need to create it
                        os.mkdir(fp)
                    if os.path.isfile(fp + '__'): # then pull this special content into the new directory
                        os.rename(fp + '__', fp + '/_')
                fp = self.filepath # reset in order to prepare to save the content

        f = codecs.open(fp, 'w+', 'utf-8')
        f.write(self.raw_content.strip())
        f.close

        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.url
        
    class Meta:
        ordering = ['url']
