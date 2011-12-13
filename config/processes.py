# This file contains processes definition for system launcher.
import os
from shared.Utils import port_randomizer


class process:
    pid = None
    command = None
    depends_on = []
    cwd = None
    debug = 0

    def __init__(self):
        pass

    def set_debug(self, debug):
        self.debug = debug
        if self.debug:
            self._handle_debug()

    def _handle_debug(self):
        pass

class services(process):
    pid = 'services'
    command = 'python'
    params = '%s/services/services_launcher.py' %os.environ['PYXIS_ROOT']


class _logger_console_manager(process):
    pid = 'logger'
    command = 'python'
    params = '%s/logger/manager.py' %os.environ['PYXIS_ROOT']

class _logger_web_manager(process):
    pid = 'logger'
    command = 'python'
    params = ['%s/logger/server.py' %os.environ['PYXIS_ROOT'], str(9997 + port_randomizer())]

class collector(process):
    pid = 'collector'
    command = 'python'
    params = '%s/collector/collector.py' %os.environ['PYXIS_ROOT']
    depends_on = [services]


class webui(process):
    pid = 'webui'
    command = 'python'
    params = ['manage.py', 'runserver', '0.0.0.0:%s' %
              (8000 + port_randomizer(),),]
    cwd = '%s/webui/' % os.environ['PYXIS_ROOT']

    def _handle_debug(self):
        self.params.append('--settings=settings_debug')


logger = _logger_console_manager

processes = (
    services(),
    logger(),
    webui(),
    collector()
)
