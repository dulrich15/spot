from __future__ import division
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db.models import *


class Student(Model):
    classroom = ForeignKey(Classroom)
    user = ForeignKey(User)

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def full_name(self):
        return '{self.last_name}, {self.first_name}'.format(self=self)

    def __unicode__(self):
        return '{self.full_name} in {self.classroom}'.format(self=self)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

