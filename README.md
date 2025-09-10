# AECMS

## Руководство по установке

### Конфигурация сайта

Клонируйте репозиторий в папку /opt:
```console
[/opt] $ git clone https://github.com/Ejudge-CMS/aecms
[/opt] $ cd aecms
```

Создайте виртуальное окружение и установите зависимости:
```console
[/opt/aecms] $ virtualenv your_env
[/opt/aecms] $ source your_env/bin/activate
(your_env) [/opt/aecms] $ pip install -r requirements.txt
```

Настройте django-приложение:
```console
(your_env) [/opt/aecms] $ ./manage.py makemigrations
(your_env) [/opt/aecms] $ ./manage.py migrate
(your_env) [/opt/aecms] $ ./manage.py collectstatic
```

Создайте суперпользователя. Укажите имя пользователя и пароль. Они вам понадобятся для работы с сайтом.
```console
(your_env) [/opt/aecms] $ ./manage.py createsuperuser
```

Добавьте имя вашего сайта в список ALLOWED_HOSTS в файле `/opt/aecms/aecms/settings.py`, а также (в целях безопасности) измените значение переменной `DEBUG` в том же файле с `True` на `False`.

#### Настройка Apache (Ubuntu)

Все команды далее выполняются от пользователя root.

Настройте права:
```console
[/opt/aecms] # chown -R your_user:www-data .
[/opt/aecms] # chmod -R 775 .
```

Создайте конфигурационный файл сайта:
```console
# vim /etc/apache2/sites-available/aecms.conf
```

Заполните его (/path/to/repo - путь до репозитория, вероятно равен /opt/aecms):
```vim
<VirtualHost *:8000>

        DocumentRoot /path/to/repo/

        ErrorLog ${APACHE_LOG_DIR}/aecms_error.log
        CustomLog ${APACHE_LOG_DIR}/aecms_access.log combined

        Alias /static /path/to/repo/static
        <Directory /path/to/repo/static>
                Require all granted
        </Directory>

        Alias /files /path/to/repo/files
        <Directory /path/to/repo/files>
                Require all granted
        </Directory>

        <Directory /path/to/repo/aecms>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        WSGIDaemonProcess alg-ej.ru python-path=/path/to/repo python-home=/path/to/repo/your_env
        WSGIProcessGroup alg-ej.ru
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptAlias / /path/to/repo/aecms/wsgi.py

</VirtualHost>
```

Разрешите порт. В файле /etc/apache2/ports.conf допишите:
```vim
...

Listen 8000

...
```

Установите модуль wsgi:

```console
# apt install libapache2-mod-wsgi-py3
# a2enmod wsgi
# systemctl restart apache2
```

Запустите сайт:
```console
# cd /etc/apache2/sites-available
[/etc/apache2/sites-available] # a2ensite aecms.conf
# systemctl reload apache2
```

Добавьте ваш хост в список-переменную ALLOWED_HOSTS в файле aecms/aecms/settings.py

### Настройка Apache (Fedora)

Все команды далее выполняются от пользователя root.

Настройте права:
```console
[/opt/aecms] # chown -R your_user:apache .
[/opt/aecms] # chmod -R 775 .
```

Создайте конфигурационный файл сайта:
```console
# vim /etc/httpd/conf.d/aecms.conf
```

Заполните его (/path/to/repo - путь до репозитория, вероятно равен /opt/aecms):
```vim
<VirtualHost *:8000>

        DocumentRoot /path/to/repo/

        ErrorLog /var/log/httpd/aecms_error.log
        CustomLog /var/log/httpd/aecms_access.log combined

        Alias /static /path/to/repo/static
        <Directory /path/to/repo/static>
                Require all granted
        </Directory>

        Alias /files /path/to/repo/files
        <Directory /path/to/repo/files>
                Require all granted
        </Directory>

        <Directory /path/to/repo/aecms>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        WSGIDaemonProcess alg-ej.ru python-path=/path/to/repo python-home=/path/to/repo/your_env
        WSGIProcessGroup alg-ej.ru
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptAlias / /path/to/repo/aecms/wsgi.py

</VirtualHost>
```

Разрешите порт. В файле /etc/httpd/conf/httpd.conf допишите:
```vim
...

Listen 8000

...
```

Установите модуль wsgi:

```console
# dnf install mod_wsgi
```

Запустите сайт:
```console
# systemctl reload httpd
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
