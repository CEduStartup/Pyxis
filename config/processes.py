# This file contains processes definition for system launcher.
import os


class process:
    pid = None
    command = None
    depends_on = []


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


processes = (services(), logger(), collector())
