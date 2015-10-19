from __future__ import division
from __future__ import unicode_literals

import codecs
import copy
import datetime
import os

from django.db.models import *

from config import page_path
from templatetags.docutils_extensions.utils import rst2xml

class Classroom(Model):
    slug = SlugField(max_length=64,unique=True)
    is_active = BooleanField(default=True)
    
    home_page = ForeignKey('Page',editable=False)
    title = CharField(max_length=256,blank=True,editable=False)
    subtitle = CharField(max_length=256,blank=True,editable=False)

    @property
    def url(self):
        return '/{}/'.format(self.slug)
        
    def save(self, args=[], kwargs={}):
        try:
            home_page = Page.objects.get(url=self.url)
        except:
            home_page = Page(url=self.url)
            home_page.save()
        
        self.home_page = home_page
        self.title = home_page.title
        self.subtitle = home_page.subtitle
            
        super(Classroom, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.slug
        
    class Meta:
        ordering = ['slug']


class Page(Model):
    url = CharField(max_length=1024,unique=True)
    parent = ForeignKey('Page',null=True,blank=True,editable=False)

    access_level = PositiveSmallIntegerField(default=0,choices=[(0,'Public'),(1,'Student'),(2,'Instructor')])
    content = TextField(blank=True)    

    title = CharField(max_length=256,blank=True,editable=False)
    subtitle = CharField(max_length=256,blank=True,editable=False)
    author = CharField(max_length=256,blank=True,editable=False)
    date = DateField(null=True,blank=True,editable=False)

    create_date = DateTimeField(auto_now_add=True)
    update_date = DateTimeField(auto_now=True)

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
        
    # @property
    # def series(self):
    #     series = []
    #     m = re.match('([\w\/]*)_(\d\d\d)$', self.pg)
    #     if m: # this page is part of a series
    #         for s in Page.objects.filter(parent=self.parent):
    #             m1 = re.match('([\w\/]*)_(\d\d\d)$', s.pg)
    #             if m1:
    #                 if m1.group(1) == m.group(1):
    #                     series.append(s)
    #     series = sorted(series, key=lambda page: page.pg)
    #     return series
    
    @property
    def filepath(self):
        filepath = os.path.abspath(os.path.join(page_path, self.url[1:]))
        if os.path.isdir(filepath):
            filepath = os.path.abspath(os.path.join(page_path, self.url[1:], '_'))
        return filepath
        
    def update(self, force_update=False): # check file system for updated version
        fp = self.filepath
        if os.path.isfile(fp):
            should_update = True
            if self.update_date:
                mod_timestamp = os.path.getmtime(fp)
                mod_datetime = datetime.datetime.fromtimestamp(mod_timestamp)
                if mod_datetime < self.update_date:
                    should_update = False
            if should_update or force_update:
                f = codecs.open(fp, 'r+', 'utf-8')
                content = f.read()
                f.close()
                self.content = content
        self.save()
        
    def save(self, args=[], kwargs={}):
        x = rst2xml(self.content)
        
        title = x.find('title')
        subtitle = x.find('subtitle')

        author = None
        date = None

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

        self.title = self.url
        if title is not None:
            self.title = title.text

        self.subtitle = ''
        if subtitle is not None:
            self.subtitle = subtitle.text
            
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
                fp = page_path
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
        f.write(self.content.strip())
        f.close

        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.url
        
    class Meta:
        ordering = ['url']
