from django.contrib.admin import *
from models import *


site.register(AssignmentCategory)

class AssignmentAdmin(ModelAdmin):
    list_filter = ['classroom']
    list_display = ['label', 'category', 'max_points', 'is_graded']

site.register(Assignment, AssignmentAdmin)
site.register(AssignmentGrade)

class AssignmentCategoryInline(TabularInline):
    model = AssignmentCategory
    extra = 0

class GradeSchemeAdmin(ModelAdmin):
    inlines = [AssignmentCategoryInline]

site.register(GradeScheme, GradeSchemeAdmin)

class AssignmentInline(StackedInline):
    model = Assignment
    extra = 0

