from wsserver.wsgi import application
from django.core.servers.basehttp import run
import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wsserver.settings")
    run('0.0.0.0', 8000, application)