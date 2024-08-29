from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpRequest
from lib.standings.standings_data import get_standings_data
from .models import *
from transliterate import translit
from django.views import View
from aecms.settings import DEFAULT_MAIN, EJUDGE_URL, EJUDGE_AUTH
from lib.judges.ejudge.registration_api import EjudgeApiSession
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt

import csv, json

class StandingsReload(View):
    def get(self, request: HttpRequest):
        if not request.user.is_superuser:
            return HttpResponseBadRequest("Not admin")
        course_id = request.GET.get('course_id')
        contest_type = request.GET.get('type')
        contests = Contest.objects.filter(course_id=course_id, type=contest_type)
        return JsonResponse({'contests': contests})

class MainView(View):
    def get(self, request, main_id=DEFAULT_MAIN):
        main = get_object_or_404(Main, id=main_id)
        courses_list = main.courses.order_by("priority")
        links = main.links.order_by("priority")
        return render(
            request,
            'main.html',
            {
                'main': main,
                'courses': courses_list,
                'links': links,
            }
        )
    
class CourseView(View):
    def get(self, request, course_label):
        course = get_object_or_404(Course, label=course_label)
        contests_list = course.contests.order_by('-date', '-id')
        links = course.links.order_by("priority")
        contests = []

        for contest in contests_list:
            contests.append({
                'contest': contest,
                'links': contest.links.order_by('id').order_by("priority"),
            })

        return render(
            request,
            'course.html',
            {
                'course': course,
                'contests': contests,
                'links': links,
                'ejudge_url': '{0}/cgi-bin/new-client?contest_id='.format(EJUDGE_URL),
                'teachers': course.teachers.order_by("priority")
            }
        )
    

class StandingsView(View):
    def get(self, request, standings_label, contest_id=-1):
        standings = get_object_or_404(Standings, label=standings_label)
        return render(
            request,
            'standings.html',
            {
                'standings': standings,
                'contest_id': contest_id,
            }
        )
    
class StandingsDataView(View):
    def get(self, request, standings_label):
        standings = get_object_or_404(Standings, label=standings_label)

        users_data, contests = get_standings_data(standings)

        return JsonResponse({
            'users': users_data,
            'contests': contests,
        })
    
class FormView(View):
    def get(self, request, form_label):
        form = get_object_or_404(FormBuilder, label=form_label)

        fields = []

        for field in form.fields.order_by("id"):
            f = {
                'id': field.id,
                'label': field.label,
                'type': field.type,
                'required': field.required,
                'internal_name': field.internal_name,
                'description': field.description,
            }
            f.update(field.TYPES_DICT)
            if field.type == FormField.SELECT:
                f['options'] = field.select_options.order_by("id")
            fields.append(f)

        print(fields)

        return render(
            request,
            'form.html',
            {
                'form': form,
                'fields': fields,
            }
        )

    @method_decorator(csrf_protect)
    def post(self, request, form_label):
        form = get_object_or_404(FormBuilder, label=form_label)
        fields = form.fields.order_by("id")
        result = dict()

        for field in fields:
            if field.type in [FormField.STR, FormField.MAIL, FormField.PHONE, FormField.LONG, FormField.DATE, FormField.SELECT]:
                result[field.internal_name] = request.POST.get(field.internal_name, '')

            if field.type == FormField.INTEGER:
                result[field.internal_name] = int(request.POST.get(field.internal_name, 0))

            if field.type == FormField.CHECKBOX:
                result[field.internal_name] = field.internal_name in request.POST
        print(result)
        name = form.register_name_template.format(**result)
        api_session = EjudgeApiSession(EJUDGE_AUTH['login'], EJUDGE_AUTH['password'], EJUDGE_URL)
        user = api_session.create_user(form.login_prefix)
        for course in form.courses:
            Participant(name=name, login=user['login'], course=course, ejudge_id=user['user_id']).save()
        result["ejudge_login"] = user["login"]
        result["ejudge_password"] = user["password"]
        result["ejudge_id"] = user["user_id"]

        return HttpResponse(form.response_text.format(**result))