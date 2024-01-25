from django.contrib import admin
from django.forms import Textarea
from django.db import models
from .models import *

class MainLinkInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = MainLink

class BigLinkInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = BigLink

@admin.register(Main)
class MainAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'title', 'subtitle']
    inlines = [BigLinkInline, MainLinkInline]

class CourseTeacherInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = Teacher

class CourseLinkInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = CourseLink

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'title', 'subtitle']
    inlines = [CourseLinkInline, CourseTeacherInline]

class ContestLinkInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = ContestLink

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'ejudge_id']
    inlines = [ContestLinkInline]

@admin.register(ParticipantGroup)
class ParticipantGroupAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'short_name']

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'name', 'login']

class FormFieldSelectOptionInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = FormFieldSelectOption

@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'label', 'type']
    inlines = [FormFieldSelectOptionInline]

class FormFieldInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = FormField

@admin.register(FormBuilder)
class FormBuilderAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'title', 'subtitle']
    inlines = [FormFieldInline]

@admin.register(EjudgeRegisterApi)
class EjudgeRegisterApiAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'label', 'login']

@admin.register(Standings)
class StandingsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    list_display = ['id', 'label', 'title']