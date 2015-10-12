from __future__ import division
from __future__ import unicode_literals

import copy

from django.db.models import *

class Classroom(Model):
    is_active = BooleanField(default=False)
    title = CharField(max_length=200)
    slug = SlugField(max_length=200)
    description = TextField(blank=True)

    def copy_instance(self):
        instance = copy.deepcopy(self)
        instance.id = None
        instance.save()

    def __unicode__(self):
        return '{self.slug}'.format(self=self)

    class Meta:
        ordering = ['-slug']
        
