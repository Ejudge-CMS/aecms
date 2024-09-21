from collections.abc import Iterable
from lib.judges.ejudge.registration_api import EjudgeApiSession
from aecms.settings import EJUDGE_AUTH, EJUDGE_URL
from django.db import models
from django.dispatch import receiver
import os

def course_teacher_path(instanse, filename):
    return 'teachers/{0}'.format(filename)

def contest_statement_path(instance, filename):
    return 'courses/{0}/statements/{1}'.format(instance.course.label, filename)

def main_link_file_path(instance, filename):
    return 'mains/{0}/links/{1}'.format(instance.main.pk, filename)

def course_link_file_path(instance, filename):
    return 'courses/{0}/links/{1}'.format(instance.course.label, filename)

def contest_link_file_path(instance, filename):
    return 'contests/{0}/links/{1}'.format(instance.contest.pk, filename)

class Course(models.Model):
    title = models.TextField(help_text='Имя курса')
    subtitle = models.TextField(help_text='Подзаголовок', blank=True)
    label = models.TextField(unique=True, help_text='Уникальная метка')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self):
        return self.title

class Main(models.Model):
    title = models.TextField(help_text='Заголовок')
    subtitle = models.TextField(help_text='Подзаголовок', blank=True)
    course_title = models.TextField(help_text='Заголовок курсов', default='Курсы')

    def __str__(self) -> str:
        return self.title
    
class Page(models.Model):
    label = models.TextField(unique=True, help_text="Уникальная метка")
    title = models.TextField(blank=True, help_text="Заголовок")
    subtitle = models.TextField(blank=True, help_text="Подзаголовок")
    is_raw = models.BooleanField(default=False, help_text="Не обрачивать в HTML и просто возвращать как текст.")
    content = models.TextField(blank=True, help_text="Содержимое в формате HTML кода")

class Teacher(models.Model):
    name = models.TextField(help_text='Название ссылки')
    course = models.ManyToManyField(Course, related_name='teachers')
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
    subtitle = models.TextField(help_text='Подзаголовок', blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, help_text='Курс', related_name='contests')
    ejudge_id = models.IntegerField(help_text='ID в Ejudge')
    contest_type = models.CharField(max_length=3, choices=ContestType.TYPES, default=ContestType.ACM, help_text='Тип контеста')
    date = models.DateField(help_text='Дата публикации')
    statements = models.FileField(blank=True, upload_to=contest_statement_path, help_text='Условия')
    duration = models.IntegerField(default=0, help_text="Длительность контеста в минутах (0 - бесконечный)")
    show_statements = models.BooleanField(default=False, help_text='Показывать условия?')

    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        if self.pk is None:
            rapi = EjudgeApiSession(EJUDGE_AUTH['login'], EJUDGE_AUTH['password'], EJUDGE_URL)
            for user in self.course.users.all():
                if user.autoregister:
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
    file = models.FileField(upload_to=contest_link_file_path, blank=True, help_text="Прикрепите файл, если хотите дать ссылку на него.")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='links')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self) -> str:
        return self.text

class CourseLink(models.Model):
    text = models.TextField(help_text='Текст ссылки')
    link = models.TextField(help_text='URL ссылки')
    file = models.FileField(upload_to=course_link_file_path, blank=True, help_text="Прикрепите файл, если хотите дать ссылку на него.")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='links')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self) -> str:
        return self.text
    
class MainLink(models.Model):
    text = models.TextField(help_text='Текст ссылки')
    link = models.TextField(help_text='URL ссылки')
    file = models.FileField(upload_to=main_link_file_path, blank=True, help_text="Прикрепите файл, если хотите дать ссылку на него.")
    main = models.ForeignKey(Main, on_delete=models.CASCADE, help_text='Страница', related_name='links')
    priority = models.IntegerField(help_text='Приоритет', default=0)

    def __str__(self) -> str:
        return self.text
    
class Participant(models.Model):
    name = models.TextField(help_text='Имя')
    login = models.TextField(help_text='Логин')
    course = models.ForeignKey(Course, related_name="users", on_delete=models.CASCADE)
    ejudge_id = models.IntegerField(help_text='ID в Ejudge')
    autoregister = models.BooleanField(help_text='Включить авторегистрацию на контесты курса?')

    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        if self.pk is None and self.autoregister:
            rapi = EjudgeApiSession(EJUDGE_AUTH['login'], EJUDGE_AUTH['password'], EJUDGE_URL)
            for contest in self.course.contests.all():
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
    register_name_template = models.TextField(help_text='Шаблон имени')
    login_prefix = models.TextField(help_text='Префикс логина')
    courses = models.ManyToManyField(Course, help_text='Курсы', related_name='forms')

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
    course = models.ForeignKey(Course, on_delete=models.CASCADE, help_text='Курс')
    contests = models.ManyToManyField(Contest, help_text='Контесты', related_name='standings')
    type = models.CharField(max_length=3, choices=ContestType.TYPES, default=ContestType.ACM)

    class Meta:
        verbose_name_plural = "Standings"

    def __str__(self):
        return "{} ({})".format(self.label, self.title)

######################################################################################################################

@receiver(models.signals.post_delete, sender=ContestLink)
def auto_delete_contest_link_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=ContestLink)
def auto_delete_contest_link_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = ContestLink.objects.get(pk=instance.pk).file
    except ContestLink.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=CourseLink)
def auto_delete_course_link_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=CourseLink)
def auto_delete_course_link_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = CourseLink.objects.get(pk=instance.pk).file
    except CourseLink.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=MainLink)
def auto_delete_main_link_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
    except:
        pass


@receiver(models.signals.pre_save, sender=MainLink)
def auto_delete_main_link_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = MainLink.objects.get(pk=instance.pk).file
    except MainLink.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=Contest)
def auto_delete_statement_file_on_delete(sender, instance, **kwargs):
    if instance.statements:
        try:
            os.remove(instance.statements.path)
        except OSError:
            pass


@receiver(models.signals.pre_save, sender=Contest)
def auto_delete_statement_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_statements = Contest.objects.get(pk=instance.pk).statements
    except Contest.DoesNotExist:
        return False
    if not old_statements:
        return False
    try:
        new_statements = instance.statements
        if not old_statements == new_statements:
            if os.path.isfile(old_statements.path):
                os.remove(old_statements.path)
    except OSError:
        pass


@receiver(models.signals.post_delete, sender=Teacher)
def auto_delete_teacher_photo_file_on_delete(sender, instance, **kwargs):
    try:
        if instance.photo:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
    except OSError:
        pass


@receiver(models.signals.pre_save, sender=Teacher)
def auto_delete_teacher_photo_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Teacher.objects.get(pk=instance.pk).photo
    except Teacher.DoesNotExist:
        return False
    if not old_file:
        return False
    try:
        new_file = instance.photo
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except OSError:
        pass