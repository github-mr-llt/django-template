# django template
> 适用于 Django 框架的微服务项目模板，该模板将项目结构和应用结构重新耦合（项目即应用），不必创建类似 base 这种名称的应用，只需创建项目即可立即编写应用，以此节省项目开发时间以及项目管理成本，同时依旧尊重传统项目结构（解耦合）。

使用模板创建 django 项目：
```bash
export TEMPLATE="https://github.com/github-mr-llt/django-template/archive/refs/heads/main.zip"
export DJANGO_TEMPLATE="--template $TEMPLATE -e md,toml"
django-admin startproject $DJANGO_TEMPLATE project_name
```

# 开始使用
安装要求：
- Redis
- Nginx 1.24+
- Python 3.10+

安装步骤：
```bash
python3 -m venv .venv --upgrade-deps
source .venv/bin/activate
pip install .[all]; rm -rf build *.egg-info
```

快速运行：
```bash
# 修改并确认 settings.py 正确
python manage.py migrate
python manage.py createsuperuser

cat > Procfile << EOF
django: python manage.py runserver
    env:
        DJANGO_SECRET_KEY: {{secret_key}}
celery: celery -A {{project_name}}.cry worker -E -B -l INFO
EOF

honcho start
```

# 关于部署
```bash
python3 -m venv .venv --upgrade-deps
source .venv/bin/activate
pip install .[all]; rm -rf build *egg-info

python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser

# uWSGI
uwsgi --ini uwsgi.ini
uwsgi --stop `grep 'pidfile' uwsgi.ini | sed 's/pidfile = //g'`
uwsgi --reload `grep 'pidfile' uwsgi.ini | sed 's/pidfile = //g'`

# Nginx
sudo link nginx.conf /etc/nginx/conf.d/project_name.conf
sudo nginx -t; sudo nginx -s reload

# Celery start and stop
celery -A project_name multi start project_name -l INFO -E -B\
    --pidfile=/usr/run/celery-%n.pid --logfile=/usr/log/celery-%n.log
kill `cat /usr/run/celery-project_name.pid`
```

uwsgi.ini
```
[uwsgi]
uid = root
gid = root
workers = 2
threads = 4
master = true
vacuum = true
chmod-socket = 777
http-keepalive = 1
max-requests = 5000

procname = {{project_name}}
chdir = {{project_directory}}
module = {{project_name}}.wsgi:application
socket = /usr/run/uwsgi-%(procname).sock
pidfile = /usr/run/uwsgi-%(procname).pid
daemonize = /usr/logs/uwsgi-%(procname).pid
# droped
# socket = %(chdir)/local/tmp/uwsgi-{{project_name}}.sock
# pidfile = %(chdir)/local/tmp/uwsgi-{{project_name}}.pid
# daemonize = %(chdir)/local/tmp/uwsgi-{{project_name}}.log

env = LANG=en_US.UTF-8
env = DJANGO_SETTINGS_MODULE={{project_name}}.settings
env = DJANGO_SECRET_KEY={{secret_key}}
```

nginx.conf
```nginx
server {
    listen                  443 ssl http2;
    listen                  [::]:443 ssl http2;
    server_name             example.com;
    set                     $base {{project_directory}};

    # SSL
    ssl_certificate         /usr/ssl_certs/example.pem;
    ssl_certificate_key     /usr/ssl_certs/example.key;
    ssl_trusted_certificate /usr/ssl_certs/example.pem;

    ssl_protocols          TLSv1.2 TLSv1.3;
    ssl_ciphers            ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

    location / {
        include                       uwsgi_params;
        uwsgi_pass                    unix:/usr/run/uwsgi-{{project_name}}.sock;
    }
    location /media/ {
        alias $base/.local/media/;
    }
    location /static/ {
        alias $base/.local/static/;
    }
    location = /favicon.ico {
        log_not_found off;
	alias $base/.local/static/favicon.ico;
    }
    location = /robots.txt {
        log_not_found off;
	alias $base/.local/static/robots.txt;
    }
}

# HTTP redirect
server {
    listen      80;
    listen      [::]:80;
    server_name .example.com;
    return 301 https://$host$request_uri;
}
```
