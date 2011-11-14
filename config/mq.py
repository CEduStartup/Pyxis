"""This file contains configuration for message queue, used in the system
The queue is used by event manager and other subsystems."""

import os


queue_host = 'localhost'
queue_port = 11300

_suffix = os.environ['LOGNAME']

LOGGER_TUBE = 'LOGGER_TUBE_%s' % (_suffix,)
COLLECTOR_TUBE = 'COLLECTOR_TUBE_%s' % (_suffix,)

