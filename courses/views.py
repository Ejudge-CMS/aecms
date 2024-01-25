from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from lib.standings.standings_data import get_standings_data
from .models import *
from transliterate import translit
from django.views import View
from aecms.settings import DEFAULT_MAIN, EJUDGE_URL, EJUDGE_AUTH
from lib.judges.ejudge.registration_api import EjudgeApiSession
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from lib.forms.form_table import get_form_columns, get_form_entry_row

import random, re, csv, json, datetime

from ipware import get_client_ip

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
    
def register_user(ejudge_register_api: EjudgeRegisterApi, name: str):
    login = ejudge_register_api.login
    api_session = EjudgeApiSession(EJUDGE_AUTH['login'], EJUDGE_AUTH['password'], EJUDGE_URL)
    int_login = True
    if ejudge_register_api.use_surname:
        surname = translit(name.split()[0], 'ru', reversed=True)
        surname = re.sub(r'\W+', '', surname).lower()
        login = f'{login}{surname}'
        int_login = False
    user = api_session.create_user(login, int_login)
    group_name = name
    p = Participant(
        name=group_name,
        login=user['login'],
        api=ejudge_register_api,
        group=ejudge_register_api.group,
        ejudge_id=user["user_id"]
    )
    print('!')
    p.save()
    return user

@method_decorator(csrf_exempt, name='dispatch')
class EjudgeRegister(View):
    def post(self, request):
        register_id = request.POST.get('register_id')
        secret = request.POST.get('secret')
        ejudge_register_api = get_object_or_404(EjudgeRegisterApi, id=register_id)
        if secret != ejudge_register_api.secret:
            return HttpResponseBadRequest("Wrong secret")
        name = request.POST.get('name')
        user = register_user(ejudge_register_api, name)
        return JsonResponse(user)
    
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

        user_ip, _ = get_client_ip(request)

        if form.requests_limit is not None and \
                form.requests_limit > 0:
            day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
            entries = len(form.entries.filter(ip=user_ip, time__gte=day_ago))
            if entries >= form.requests_limit:
                return HttpResponse("Превышенно максимальное число запросов")

        for field in fields:
            if field.type in [FormField.STR, FormField.MAIL, FormField.PHONE, FormField.LONG, FormField.DATE, FormField.SELECT]:
                result[field.internal_name] = request.POST.get(field.internal_name, '')

            if field.type == FormField.INTEGER:
                result[field.internal_name] = int(request.POST.get(field.internal_name, 0))

            if field.type == FormField.CHECKBOX:
                result[field.internal_name] = field.internal_name in request.POST
        print(result)
        name = form.register_name_template.format(**result)
        ejudge_register_api = form.register_api
        user_login = register_user(ejudge_register_api, name)
        result["ejudge_login"] = user_login["login"]
        result["ejudge_password"] = user_login["password"]
        result["ejudge_id"] = user_login["user_id"]

        entry = FormEntry.objects.create(form=form, data=json.dumps(result), ip=user_ip)
        entry.save()

        return HttpResponse(form.response_text.format(**result))
        
class FormDataView(View):
    def get(self, request):
        user = request.user
        if not user.is_superuser:
            return HttpResponseBadRequest("Not admin")
        forms = FormBuilder.objects.order_by("-id")
        res = []
        for form in forms:
            res.append(dict())
            res[-1]["form"] = form
            res[-1]["entries"] = len(form.entries.all())

        return render(
            request,
            'form_data.html',
            {
                "forms": res
            }
        )


class FormJsonExport(View):
    def get(self, request, form_label):
        user = request.user
        if not user.is_superuser:
            return HttpResponseBadRequest("Not admin")

        form = get_object_or_404(FormBuilder, label=form_label)

        entries = form.entries.order_by("id")

        result = []
        for entry in entries:
            entry_dict = json.loads(entry.data)
            entry_dict["ip"] = entry.ip
            entry_dict["time"] = entry.time.isoformat()
            result.append(entry_dict)

        return JsonResponse(result, safe=False)


class FormCSVExport(View):
    def get(self, request, form_label):
        user = request.user
        if not user.is_superuser:
            return HttpResponseBadRequest("Not admin")

        form = get_object_or_404(FormBuilder, label=form_label)

        response = HttpResponse(
            content_type='text/csv',
        )

        response['Content-Disposition'] = 'attachment; filename="{label}.csv"'.format(label=form.label)
        writer = csv.writer(response)

        columns, column_names = get_form_columns(form)

        writer.writerow(columns)

        entries = form.entries.order_by("id")

        for entry in entries:
            writer.writerow(get_form_entry_row(entry, column_names))

        return response