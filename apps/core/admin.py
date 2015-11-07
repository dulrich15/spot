from django.contrib.admin import *
from models import *

class ClassroomAdmin(ModelAdmin):
    def toggle_active(self, request, queryset):
        for classroom in queryset:
            classroom.is_active = not(classroom.is_active)
            classroom.save()
            if classroom.is_active:
               self.message_user(request, 'Classroom {0} has been made active'.format(classroom))
            else:
               self.message_user(request, 'Classroom {0} has been made inactive'.format(classroom))
    toggle_active.short_description = 'Toggle is_active flag'

    list_display = ['title','is_active']
    readonly_fields = ['title','subtitle','instructor','first_date','banner_link']
    actions = ['toggle_active']

site.register(Classroom, ClassroomAdmin)

class PageAdmin(ModelAdmin):
    readonly_fields = ['create_date','last_update','print_template','access_level','title','subtitle','author','date','parent']

site.register(Page,PageAdmin)
