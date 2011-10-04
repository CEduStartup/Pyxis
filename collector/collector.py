import gevent
import sys
import time
import traceback

import config.collector as collector_config
import config.storage as storage_config

from EventSender import sender
from gevent.backdoor import BackdoorServer
from shared.events import Event
from Scheduler import Scheduler
from storage import storage_types
from TrackerCollection import TrackerCollection


def initialize():
    """Initialize all requred components
    """
    global storage, scheduler, tracker_collection

    storage_class = storage_types[storage_config.storage_type]

    storage = storage_class(storage_config.host, storage_config.port,
                        storage_config.db_name)
    sender.fire('COLLECTOR.WORKFLOW', message='Storage created.')

    sender.fire('COLLECTOR.WORKFLOW', message='Storage created.')

    scheduler = Scheduler()
    sender.fire('COLLECTOR.WORKFLOW', message='Scheduler created.')

    tracker_collection = TrackerCollection(scheduler, storage)
    sender.fire('COLLECTOR.WORKFLOW', message='TrackerCollection created.')


def run():
    """Implement main logic.
    """
    tracker_collection.start()
    sender.fire('COLLECTOR.WORKFLOW', message='TrackerCollection started.')

    storage.start()
    sender.fire('COLLECTOR.WORKFLOW', message='Storage started.')

    scheduler.start()
    sender.fire('COLLECTOR.WORKFLOW', message='Scheduler started.')

def handle_command_line_args():
    HELP = '--help'

    if HELP in sys.argv:
        print """\
Options:
--help - print this message without running app.
"""
        exit()


def initialize_backdoor():
    """Initialize backdoor server.
    """
    host = collector_config.backdoor_host
    port = collector_config.backdoor_port

    sender.fire('COLLECTOR.WORKFLOW',
                message='Initializing backdoor on %s:%s' % (host, port))
    BackdoorServer((host, port)).serve_forever()


if __name__ == '__main__':
    handle_command_line_args()

    try:
        initialize()
        run()
        initialize_backdoor()
    except Exception:
        # Here we need to handle all errors which are not handled by any
        # component above.
        sender.fire('LOGGER.CRITICAL',
                    message='collector unhandled error: %s' %
                       (traceback.format_exc(),))
        sys.exit(-1)

