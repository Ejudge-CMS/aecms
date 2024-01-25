from collections.abc import Iterable
from lib.judges.ejudge.registration_api import EjudgeApiSession
from aecms.settings import EJUDGE_AUTH, EJUDGE_URL
from django.db import models

def course_teacher_path(instanse, filename):
    return 'course_{0}/teachers/{1}'.format(instanse.course.label, filename)

def contest_statement_path(instance, filename):
    return 'course_{0}/contests/contest_{1}/{2}'.format(instance.course.label, instance.id, filename)

class Course(models.Model):
    title = models.TextField(help_text='Имя курса')
    subtitle = models.TextField(help_text='Подзаголовок', blank=True)
    label = models.TextField(unique=True, help_text='Уникальная метка')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self):
        return "{} ({})".format(self.title, self.id)

class Main(models.Model):
    title = models.TextField(help_text='Заголовок')
    subtitle = models.TextField(help_text='Подзаголовок', blank=True)
    course_title = models.TextField(help_text='Заголовок курсов', default='Курсы')

    def __str__(self) -> str:
        return self.title

class Teacher(models.Model):
    name = models.TextField(help_text='Название ссылки')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='teachers')
    photo = models.FileField(upload_to=course_teacher_path, help_text='Фото')
    telegram_id = models.TextField(blank=True, help_text='Telegram ID')
    vk_id = models.TextField(blank=True, help_text='VK ID')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self) -> str:
        return self.name
    
class ContestType:
    OLYMP = "OLP"
    ACM = "ACM"

    TYPES = (
        (OLYMP, "OLP"),
        (ACM, "ACM")
    )

    TYPES_DICT = {
        "OLP": OLYMP,
        "ACM": ACM
    }
    
class Contest(models.Model, ContestType):
    name = models.TextField(help_text='Название контеста')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, help_text='Курс', related_name='contests')
    ejudge_id = models.TextField(help_text='ID в Ejudge')
    contest_type = models.CharField(max_length=3, choices=ContestType.TYPES, default=ContestType.ACM, help_text='Тип контеста')
    date = models.DateField(help_text='Дата публикации')
    statements = models.FileField(blank=True, upload_to=contest_statement_path, help_text='Условия')
    duration = models.IntegerField(default=0, help_text="Длительность контеста в минутах")
    show_statements = models.BooleanField(default=False, help_text='Показывать условия?')

    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:

        if self.pk is None:
            users = []
            for api in self.course.apis.all():
                users.extend(api.users.all())
            rapi = EjudgeApiSession(EJUDGE_AUTH['login'], EJUDGE_AUTH['password'], EJUDGE_URL)
            for user in users:
                rapi.add_registration(user.ejudge_id, user.login, self.ejudge_id, user.name)

        return super().save()

    def __str__(self) -> str:
        return self.name
    
class BigLink(models.Model):
    text = models.TextField(help_text='Текст ссылки')
    link = models.TextField(help_text='URL ссылки')
    main = models.ForeignKey(Main, on_delete=models.CASCADE, help_text='Страница', related_name='courses')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self) -> str:
        return self.text
    
class ContestLink(models.Model):
    text = models.TextField(help_text='Текст ссылки')
    link = models.TextField(help_text='URL ссылки')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='links')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self) -> str:
        return self.text

class CourseLink(models.Model):
    text = models.TextField(help_text='Текст ссылки')
    link = models.TextField(help_text='URL ссылки')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='links')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self) -> str:
        return self.text
    
class MainLink(models.Model):
    text = models.TextField(help_text='Текст ссылки')
    link = models.TextField(help_text='URL ссылки')
    main = models.ForeignKey(Main, on_delete=models.CASCADE, help_text='Страница', related_name='links')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self) -> str:
        return self.text
    
class ParticipantGroup(models.Model):
    name = models.TextField(help_text='Название группы')
    short_name = models.TextField(help_text='Название для standings')

    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.id)
    
class EjudgeRegisterApi(models.Model):
    label = models.TextField(unique=True, help_text='Название')
    secret = models.TextField(help_text='Секретный код')
    login = models.TextField(help_text='Префикс логина')
    use_surname = models.BooleanField(default=False, help_text='Использовать имя в логине?')
    group = models.ForeignKey(ParticipantGroup, help_text='Регистрации', related_name='apis', on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, help_text='Курсы', related_name='apis')

    def __str__(self) -> str:
        return self.label
    
class Participant(models.Model):
    name = models.TextField(help_text='Имя')
    login = models.TextField(help_text='Логин')
    group = models.ForeignKey(ParticipantGroup, related_name='users', on_delete=models.CASCADE)
    api = models.ForeignKey(EjudgeRegisterApi, related_name='users', on_delete=models.CASCADE)
    ejudge_id = models.IntegerField(help_text='ID в Ejudge')

    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:

        if self.pk is None:
            contests = []
            for course in self.api.courses.all():
                contests.extend(course.contests.all())
            rapi = EjudgeApiSession(EJUDGE_AUTH['login'], EJUDGE_AUTH['password'], EJUDGE_URL)
            for contest in contests:
                rapi.add_registration(self.ejudge_id, self.login, contest.ejudge_id, self.name)

        return super().save()

    def __str__(self) -> str:
        return self.name
    
class FormBuilder(models.Model):
    label = models.TextField(unique=True, help_text='Название')
    title = models.TextField(help_text='Заголовок')
    subtitle = models.TextField(help_text='Подзаголовок', blank=True)
    button_text = models.TextField(default="Отправить", help_text='Текст на кнопке')
    response_text = models.TextField(help_text='Шаблон результата')
    requests_limit = models.IntegerField(help_text='Лимит запросов на день', blank=True, null=True)
    register_name_template = models.TextField(help_text='Шаблон имени')
    register_api = models.ForeignKey(EjudgeRegisterApi, help_text='Шаблон регистрации', on_delete=models.CASCADE, related_name='forms')

    def __str__(self) -> str:
        return self.label
    
class FormFieldType:
    STR = "ST"
    INTEGER = "IN"
    MAIL = "ML"
    PHONE = "PH"
    DATE = "DT"
    LONG = "LO"
    CHECKBOX = "CB"
    TEXT = "TX"
    SELECT = "SL"

    TYPES = (
        (STR, "Small text field"),
        (INTEGER, "Number"),
        (MAIL, "Mail address"),
        (PHONE, "Phone number"),
        (DATE, "Date"),
        (LONG, "Large textarea"),
        (CHECKBOX, "Check box"),
        (TEXT, "Text without field"),
        (SELECT, "Select")
    )

    TYPES_DICT = {
        "STR": STR,
        "INTEGER": INTEGER,
        "MAIL": MAIL,
        "PHONE": PHONE,
        "DATE": DATE,
        "LONG": LONG,
        "CHECKBOX": CHECKBOX,
        "TEXT": TEXT,
        "SELECT": SELECT,
    }

class FormEntry(models.Model):
    form = models.ForeignKey(FormBuilder, related_name="entries", on_delete=models.CASCADE)
    data = models.TextField()
    ip = models.TextField(blank=True)
    time = models.DateTimeField(auto_now_add=True)
    
class FormField(models.Model, FormFieldType):
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE, help_text='Форма', related_name='fields')
    label = models.TextField(unique=True, help_text='Название')
    type = models.CharField(max_length=2, choices=FormFieldType.TYPES, default=FormFieldType.STR, help_text='Тип')
    required = models.BooleanField(default=False, help_text='Обязательное поле?')
    internal_name = models.TextField(help_text='Полное название')
    description = models.TextField(blank=True, help_text='Описание')


class FormFieldSelectOption(models.Model):
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, help_text='Поле', related_name='options')
    label = models.TextField(help_text='Текст')

class Standings(models.Model, ContestType):
    title = models.TextField(help_text='Заголовок')
    label = models.TextField(unique=True, help_text='Идентификатор')
    groups = models.ManyToManyField(ParticipantGroup, help_text='Группы', related_name='standings')
    contests = models.ManyToManyField(Contest, help_text='Контесты', related_name='standings')
    contest_type = models.CharField(max_length=3, choices=ContestType.TYPES, default=ContestType.ACM)

    class Meta:
        verbose_name_plural = "Standings"

    def __str__(self):
        return "{} ({})".format(self.label, self.title)