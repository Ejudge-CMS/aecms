# AECMS

## Руководство по установке

Клонируйте репозиторий:
```console
$ git clone https://github.com/Semen-prog/aecms
$ cd aecms
```

Создайте виртуальное окружение и установите зависимости:
```console
[aecms] $ virtualenv your_env
[aecms] $ source your_env/bin/activate
(your_env) [aecms] $ pip install -r requirements.txt
```

Настройте django-приложение:
```console
(your_env) [aecms] $ ./manage.py makemigrations
(your_env) [aecms] $ ./manage.py migrate
(your_env) [aecms] $ ./manage.py collectstatic
```

Создайте суперпользователя. Укажите имя пользователя и пароль. Они вам понадобятся для работы с сайтом.
```console
(your_env) [aecms] $ ./manage.py createsuperuser
```

## Настройка Apache

Все команды далее выполняются от пользователя root.

Настройте права:
```console
[aecms] # chown -R :www-data .
[aecms] # chmod -R 775 .
```

Создайте конфигурационный файл сайта:
```console
# vim /etc/apache2/sites-available/aecms.conf
```

Заполните его:
```vim
<VirtualHost *:8000>

        DocumentRoot /path/to/repo/aecms/

        ErrorLog ${APACHE_LOG_DIR}/aecms_error.log
        CustomLog ${APACHE_LOG_DIR}/aecms_access.log combined
        Alias /static /path/to/repo/aecms/static
        <Directory /path/to/repo/aecms/static>
                Require all granted
        </Directory>

        <Directory /path/to/repo/aecms/aecms>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        WSGIDaemonProcess alg-ej.ru python-path=/path/to/repo/aecms python-home=/path/to/repo/aecms/cms
        WSGIProcessGroup alg-ej.ru
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptAlias / /path/to/repo/aecms/aecms/wsgi.py

</VirtualHost>
```

Разрешите порт. В файле /etc/apache2/ports.conf допишите:
```vim
...

Listen 8000

...
```

Запустите сайт:
```console
# a2ensite /etc/apache2/sites-available/aecms.conf
```

## Конфигурационный файл

Теперь надо подредактировать файл configs/config.json.

Поля:

1. *login* - логин админа в ejudge.
2. *password* - пароль админа в ejudge.
3. *url* - url, по которому доступен ejudge.
4. *judges-dir* - место, куда сохраняются контесты (по умолчанию - /home/judges).
5. *external-dir* - место, куда сохраняются результаты (в современных версиях ejudge - /var/lib/ejudge/status).
6. *main* - ID Main-страницы, которая будет показываться по адресу http://your_ip:8000 (как только вы ее создадите).