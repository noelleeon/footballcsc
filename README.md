# https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-22-04
# This project template was built from the following link which features a django project build walkthrough
# https://www.w3schools.com/django/index.php
# Also referencing the following link
# https://www.youtube.com/watch?v=nGIg40xs9e4&t=103s

# This project was created after making a droplet on DigitalOcean in
# the image of Ubuntu. This project also uses a hosted mysql database on
# DigitalOcean. This project was made on ubuntu by ssh into the ip address
# produced by the DigitalOcean droplet.
# domain (blitz3d.net) hosted by go daddy and points to digital ocean droplet public ipv4 

# /////////////////////////////////////////////////////////////////////////////
# ////////////////COMPONENTS OUTSIDE OF THIS APPLICATION BUILD/////////////////
# /////////////////////////////////////////////////////////////////////////////
# I made a droplet on digital ocean
# I made a hosted database on that droplet
# I bought a domain from go daddy http://blitz3d.net
# https straight out the gate was too expensive

# I bought an SSL cert from go daddy and configured it in my
# /etc/nginx/sites-enabled/footballproj.conf file
# I also generated a private key because you need both in that file


# /////////////////////////////////////////////////////////////////////////////
# ////////////////////////FOOTBALL DATA STUFF//////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
source: https://pypi.org/project/nfl-data-py/#description
pip install nfl_data_py
results in:
Installing collected packages: pytz, appdirs, six, numpy, fsspec, cramjam, python-dateutil, pandas, fastparquet, nfl_data_py
Successfully installed appdirs-1.4.4 cramjam-2.9.0 fastparquet-2024.11.0 fsspec-2024.10.0 nfl_data_py-0.3.3 numpy-1.26.4 pandas-1.5.3 python-dateutil-2.9.0.post0 pytz-2024.2 six-1.17.0

source: https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl
This is for the live play by play data

I did gzip in nginx and am also using celery because some of the payload
is very large
pip install celery
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////


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

# /////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////GITHUB/////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
git init
git add .
git commit -m "your message"
git branch -M main
git remote add origin git remote add origin https://noelleeon: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@github.com/noelleeon/footballcsc.git
git push -u origin main --force
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////Create django project///////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# Install Django
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install Django

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
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////GUNICORN/////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
source: https://www.youtube.com/watch?v=Td3lirXIeRI&t=2206s
file: .venv/bin/gunicorn_start:
#!/bin/bash -x

export NAME='footballproj'
export DJANGODIR=/home/footballproj
export SOCKFILE=/home/footballproj/run/gunicorn.sock
export USER=footballproj
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
command = /home/footballproj/.venv/bin/gunicorn_start
user = footballproj
stderr_logfile = /home/footballproj/logs/supervisor.log
stdout_logfile = /home/footballproj/logs/supervisor.log
redirect_stderr = true
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8

# to run this conf
supervisorctl reread
supervisorctl update
supervisorctl status
# should print out something like this:
footballproj                     RUNNING   pid 35275, uptime 0:00:18
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////NGINX STUFF/////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# go to sites-available and add file
cd /etc/nginx/sites-available
vim footballproj.conf

upstream footballproj_app_server {
        server unix:/home/footballproj/run/gunicorn.sock fail_timeout=0;
}

server {
        listen 80;
        server_name blitz3d.net www.blitz3d.net;
        access_log /home/footballproj/logs/access.log;
        error_log /home/footballproj/logs/error.log;
        return 301 https://$host$request_uri;
}
server {
        listen 443 ssl;
        server_name blitz3d.net www.blitz3d.net;
        ssl_certificate /etc/ssl/certs/combinedcert.pem;
        ssl_certificate_key /etc/ssl/private/pkey.txt;

        location /static/ {
                alias /home/footballproj/static/;
        }

        location /media/ {
                alias /home/footballproj/media/;
        }

        location / {
                add_header 'Access-Control-Allow-Origin' 'http://www.blitz3d.net' always;
                add_header 'Access-Control-Allow-Credentials' 'true' always;
                add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
                add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With' always;

                # if preflight request, we will cache it
                if ($request_method = 'OPTIONS') {
                  add_header 'Access-Control-Max-Age' 1728000;
                  add_header 'Content-Type' 'text/plain charset=UTF-8';
                  add_header 'Content-Length' 0;
                  return 204;
                }

                proxy_pass http://unix:/home/footballproj/run/gunicorn.sock;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
        }
}

# go to sites-enabled
cd /etc/nginx/sites-enabled
# make symbolic link
ln -s ../sites-available/footballproj.conf .
# check that nginx will compile with no errors
nginx -t
# in /etc/nginx/nginx.conf I followed this demo
# some of the football apis have a massive payload
# this is supposed to help with that latency
source: https://www.digitalocean.com/community/tutorials/how-to-improve-website-performance-using-gzip-and-nginx-on-ubuntu-20-04#step-4-verifying-the-new-configuration
source: https://stackoverflow.com/questions/29823422/compressing-the-response-payload-in-django-rest

# while still in sites-enabled directory start nginx
sudo systemctl start nginx
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////Install dependancies////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# Install mysql: The chosen database
pip install mysqlclient 
# Install bootstrap: it is easier to do links in html with this
# https://www.w3schools.com/django/django_add_bootstrap5.php
pip install django-bootstrap-v5

# /////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////OPEN AI//////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
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
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////


# https://www.photondesigner.com/articles/instant-messenger?ref=rdjango-instant-messenger
# https://www.digitalocean.com/community/questions/enable-remote-redis-connection
# https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-22-04

# /////////////////////////////////////////////////////////////////////////////
# ////////////////////////////LIVE CHAT COMPONENTS/////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
# https://simpy.readthedocs.io/en/latest/simpy_intro/installation.html
# Install the live chat junk
sudo apt install python3-simpy
source: https://www.geeksforgeeks.org/realtime-chat-app-using-django/
-From 4.0.0 on of channels you need daphne
pip install -U channels
pip install -U daphne
-Add channels and daphne to installed apps in settings.py

# Add this to asgi.py file
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

# ////////////REDIS STUFF///////////////
# https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-22-04
# In redis.conf:
 rename-command FLUSHDB FLUSHDBA
 rename-command FLUSHALL FLUSHALLB
 rename-command KEYS KEYSC                                                   rename-command PEXPIRE PEXPIRED                                             rename-command DEL DELE                                                     rename-command CONFIG CONFIGF                                               rename-command SHUTDOWN SHUTDOWNG                                           rename-command BGREWRITEAOF BGREWRITEAOFH                                   rename-command BGSAVE BGSAVEI                                               rename-command SAVE SAVEJ                                                   rename-command SPOP SPOPK                                                   rename-command SREM SREML                                                   rename-command RENAME RENAMEM                                               rename-command DEBUG DEBUGN 

 requirepass V34dOa3y1VwsOZVXjhD7ZN0NRjL0q10y4prHNdGdchXODcV2pbtr25/NUpKG9FyMcAafZSqxf690n8q7
# /////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////
