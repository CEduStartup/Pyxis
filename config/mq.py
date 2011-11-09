"""This file contains configuration for message queue, used in the system
The queue is used by event manager and other subsystems."""

import os


queue_host = 'localhost'
queue_port = 11300

LOGGER_TUBE = 'LOGGER_TUBE_%s' % (os.environ['LOGNAME'],)
