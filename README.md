# This project template was built from the following link which features a django project build walkthrough
# https://www.w3schools.com/django/index.php
# Also referencing the following link
# https://www.youtube.com/watch?v=nGIg40xs9e4&t=103s

# This project was created after making a droplet on DigitalOcean in
# the image of Ubuntu. This project also uses a hosted mysql database on
# DigitalOcean. This project was made on ubuntu by ssh into the ip address
# produced by the DigitalOcean droplet.
# domain (blitz3d.net) hosted by go daddy and points to digital ocean droplet public ipv4 


# IF PIP IS BEING TRASH DO THIS
(.venv) root@footballcscdroplet:~/footballproj# deactivate
root@footballcscdroplet:~/footballproj# rm -rf .venv
root@footballcscdroplet:~/footballproj# python3 -m venv .venv
root@footballcscdroplet:~/footballproj# source .venv/bin/activate
(.venv) root@footballcscdroplet:~/footballproj# which pip
/root/footballproj/.venv/bin/pip
(.venv) root@footballcscdroplet:~/footballproj# which python
/root/footballproj/.venv/bin/python
(.venv) root@footballcscdroplet:~/footballproj# 

# /////////GITHUB/////////////
git init
git add .
git commit -m "your message"
git branch -M main
git remote add origin git remote add origin https://noelleeon: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@github.com/noelleeon/footballcsc.git
git push -u origin main --force

# Install Djangoi
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install Django

# /////////GUNICORN/////////
source: https://www.youtube.com/watch?v=Td3lirXIeRI&t=2206s
file: .venv/bin/gunicorn_start:
#!/bin/bash -x

export NAME='footballproj'
export DJANGODIR=/root/footballproj
export SOCKFILE=/root/footballproj/run/gunicorn.sock
export USER=root
export GROUP=footballproj
export NUM_WORKERS=5
export DJANGO_SETTINGS_MODULE=footballproj.settingsprod
export DJANGO_WSGI_MODULE=footballproj.wsgi
export TIMEOUT=120

cd $DJANGODIR
source .venv/bin/activate
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

exec .venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
        --name $NAME \
        --workers $NUM_WORKERS \
        --timeout $TIMEOUT \
        --user=$USER --group=$GROUP \
        --bind=unix:$SOCKFILE \
        --log-level=debug \
        --log-file=-
# To run the file:
.venv/bin/gunicorn_start

# In /etc/supervisor/conf.d/footballproj.conf
[program:footballproj]
command = /root/footballproj/.venv/bin/gunicorn_start
user = root
stdou_logfile = /root/footballproj/logs/supervisor.log
redirect_stderr = true
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8

# to run this conf
supervisorctl reread
supervisorctl update
supervisorctl status
# should print out something like this:
footballproj                     RUNNING   pid 35275, uptime 0:00:18


# //////////NGINX STUFF/////////////
# go to sites-available and add file
cd /etc/nginx/sites-available
vim footballproj.conf

upstream footballproj_app_server {
        server unix:/root/footballproj/run/gunicornsock fail_timeout=0;
}

server {
        listen 80;
        server_name blitz3d.com;
        access_log /root/footballproj/logs/access.log;
        error_log /root/footballproj/logs/error.log;
        
        location /static/ {
                alias /root/footballproj/static/;
        }       
        
        location /media/ {
                alias /root/footballproj/media/;
        }       
        
        location / {
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header Host $http_host;
                proxy_redirect off;
                if (!-f $request_filename) {
                        proxy_pass http://footballproj_app_server;
                }       
        }   
}

# go to sites-enabled
cd /etc/nginx/sites-enabled
# make symbolic link
ln -s ../sites-available/footballproj.conf .
# while still in sites-enabled directory start nginx
service nginx start


# Create project 
django-admin startproject footballproj
(This makes a sub directory footballproj which will be in the same folder as manage.py)
(This will contain these files:
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
)

# Create app
py manage.py startapp fbapp
(this makes a sub directory fbapp which will be in the same folder as manager.py)
(This will contain these files:
        migrations/
            __init__.py
        __init__.py
        admin.py
        apps.py
        models.py
        tests.py
        views.py
)
-views.py is where all of the http requests and responses go 
-urls.py is where you declare the url patterns/paths

# Create template folder in fbapp
    manage.py
    footballproj/
    fbapp/
        templates/
            myfirst.html

# To run the server
-Go to the base folder
python3 manage.py runserver

# Change the settings
-Go to: /footballproj/settings.py
-Write the name of the application in here
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fbapp'
]
-Run the migrate command
python3 manage.py migrate
-Run the server and the html should render

# Install mysql
pip install mysqlclient

# ///////OPEN AI//////
source: https://platform.openai.com/docs/api-reference/introduction
# To install open ai
pip install openai
source: https://platform.openai.com/docs/quickstart
# Create an api key on open ai and place in .env file
export OPEN_API_KEY="thekey"
source: https://pypi.org/project/python-dotenv/
# Install dotenv to do environment stuff
pip install python-dotenv
# Implement open ai stuff in the views.py file


# ////////LIVE CHAT COMPONENTS////////
source: https://www.geeksforgeeks.org/realtime-chat-app-using-django/
-From 4.0.0 on of channels you need daphne
pip install -U channels
pip install -U daphne
-Add channels and daphne to installed apps in settings.py
-Add this to asgi.py file
import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "footballproj.settings")
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Just HTTP for now. (We can add other protocols later.)
})

ASGI_APPLICATION = 'footballproj.asgi.application'
