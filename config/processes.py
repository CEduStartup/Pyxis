# This file contains processes definition for system launcher.
import os
import settings


class process:
    pid = None
    command = None
    depends_on = []
    cwd = None


class services(process):
    pid = 'services'
    command = 'python'
    params = '%s/services/services_launcher.py' %os.environ['PYXIS_ROOT']


class logger(process):
    pid = 'logger'
    command = 'python'
    params = '%s/logger/manager.py' %os.environ['PYXIS_ROOT']


class collector(process):
    pid = 'collector'
    command = 'python'
    params = '%s/collector/collector.py' %os.environ['PYXIS_ROOT']
    depends_on = [services]


class webui(process):
    pid = 'webui'
    command = 'python'
    params = ['manage.py', 'runserver']
    #params = ['manage.py', 'runserver', '0.0.0.0:7777']
    cwd = '%s/webui/' % os.environ['PYXIS_ROOT']

processes = (
    services,
    logger,
    webui,
    #collector
)