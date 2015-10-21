from django.contrib.admin import *
from models import *

class ClassroomAdmin(ModelAdmin):
    readonly_fields = ['title','subtitle','banner_link']
    # fields = ['classroom', 'banner_filename', 'banner_link', 'is_active']

site.register(Classroom, ClassroomAdmin)

class PageAdmin(ModelAdmin):
    readonly_fields = ['title','subtitle','author','date','parent']

site.register(Page,PageAdmin)
