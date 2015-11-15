from __future__ import division
from __future__ import unicode_literals

from django.db.models import *

from apps.core.models import Classroom
from apps.core.models import Student


class GradeScheme(Model):
    classroom = OneToOneField(Classroom)

    def get_student_grade(self, student):
        overall = 0
        weights = 0
        subtotals = dict()
        for category in AssignmentCategory.objects.filter(scheme=self):
            tot_pts = 0
            max_pts = 0
            for assignment in Assignment.objects.filter(category=category):
                if assignment.is_graded:
                    for grade in AssignmentGrade.objects.filter(assignment=assignment,student=student):
                        if not grade.is_excused:
                            tot_pts += grade.total_points
                            max_pts += assignment.max_points
            if max_pts:
                subtotals[category] = tot_pts / max_pts
                overall += category.weight * subtotals[category]
                weights += category.weight
                
        if weights:
            overall = overall / weights
            
        return overall, subtotals

    def dump_student_grade(self, student):
        csv = []
        for category in AssignmentCategory.objects.filter(scheme=self):
            for assignment in Assignment.objects.filter(category=category):
                pts = ''
                if assignment.is_graded:
                    for grade in AssignmentGrade.objects.filter(assignment=assignment,student=student):
                        if not grade.is_excused:
                            pts = str(grade.total_points)
                csv.append(pts)
        return ','.join(csv)

    def dump_assignment_labels(self):
        csv_labels = []
        for category in AssignmentCategory.objects.filter(scheme=self):
            for assignment in Assignment.objects.filter(category=category):
                csv_labels.append(assignment.label)
        return ','.join(csv_labels)
        
    def __unicode__(self):
        return '{self.classroom}'.format(self=self)

    class Meta:
        ordering = ['classroom']


class AssignmentCategory(Model):
    scheme = ForeignKey(GradeScheme)
    name = CharField(max_length=200)
    weight_raw = PositiveSmallIntegerField(default=1)

    # if_missing_use = ForeignKey('AssignmentGradeWeight',null=True,blank=True,related_name='*')
    # drop_worst = BooleanField(default=False)
    # drop_best = BooleanField(default=False)
    # notes = TextField(null=True, blank=True)

    @property
    def weight(self):
        o = self.__class__.objects.filter(scheme=self.scheme)
        tot = sum([gw.weight_raw for gw in o])
        return self.weight_raw / tot

    @property
    def label(self):
        return '{self.name} at {self.weight:.0%}'.format(self=self)

    def __unicode__(self):
        return '{self.scheme.classroom} | {self.label}'.format(self=self)

    class Meta:
        ordering = ['scheme', '-weight_raw', 'name']
        verbose_name_plural = 'assignment categories'


class Assignment(Model):
    classroom = ForeignKey(Classroom)
    category = ForeignKey(AssignmentCategory)
    title = CharField(max_length=200, null=True, blank=True)
    due_date = DateField(null=True, blank=True)
    max_points = PositiveSmallIntegerField(default=0)
    curve_points = PositiveSmallIntegerField(default=0)
    is_graded = BooleanField(default=False)

    @property
    def label(self):
        if self.title:
            return self.title
        else:
            return self.category

    @property
    def date_due(self):
        if self.due_date:
            return self.due_date
        else:
            return self.classroom.last_day

    @property
    def grades(self):
        grades = []
        for student in Student.objects.filter(classroom=self.classroom):
            try:
                grade = AssignmentGrade.objects.get(assignment=self, student=student)
            except:
                class grade(object):
                    pass
            grade.student = student
            grades.append(grade)
        return grades

    @property
    def average(self):
        nbr = 0
        pts = 0
        max = 0
        for grade in self.grades:
            if grade.total_points > 0:
                nbr += 1
                pts += grade.total_points
                max += self.max_points
        if nbr:
            return {
                'pts' : pts / nbr,
                'max' : max / nbr, 
                'pct' : pts / max
            }
        else:
            return None
        
    def __unicode__(self):
        return '{self.label} in {self.classroom}'.format(self=self)

    class Meta:
        ordering = ['category', 'due_date']


class AssignmentGrade(Model):
    assignment = ForeignKey(Assignment)
    student = ForeignKey(Student)
    earned_points = PositiveSmallIntegerField(default=0)
    extra_points = PositiveSmallIntegerField(default=0)
    is_excused = BooleanField(default=False)

    @property
    def total_points(self):
        return self.earned_points + self.extra_points + self.assignment.curve_points

    @property
    def percent(self):
        if self.assignment.max_points: # when wouldn't it be there, really?
            return self.total_points / self.assignment.max_points
        else:
            return None

    def __unicode__(self):
        return '{self.assignment.label} for {self.student}'.format(self=self)

    class Meta:
        ordering = ['assignment__category', 'assignment']

