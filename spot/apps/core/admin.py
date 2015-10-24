from django.contrib.admin import *
from models import *

class ClassroomAdmin(ModelAdmin):
    readonly_fields = ['title','subtitle','instructor','first_date','banner_link']

site.register(Classroom, ClassroomAdmin)

class PageAdmin(ModelAdmin):
    readonly_fields = ['create_date','last_update','print_template','access_level','title','subtitle','author','date','parent']

site.register(Page,PageAdmin)
