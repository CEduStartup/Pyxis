import sys
import traceback

import config.collector as collector_config
import config.storage as storage_config

from config.init.trackers import sender
from gevent.backdoor import BackdoorServer
from Scheduler import Scheduler
from storage import storage_types
from TrackerCollection import TrackerCollection


storage = None
tracker_collection = None
scheduler = None


def initialize():
    """Initialize all requred components
    """
    global storage, scheduler, tracker_collection

    storage_class = storage_types[storage_config.storage_type]
    storage = storage_class(storage_config.host, storage_config.port,
                        storage_config.db_name)
    scheduler = Scheduler()
    tracker_collection = TrackerCollection(scheduler, storage)

def _start_srv(service, name):
    """Helper function to start service.
    """
    service.start()
    sender.fire('COLLECTOR.SERVICE_STARTED.SUCCESS',
                srv_name=name)

def run():
    """Implement main logic.
    """
    _start_srv(storage, 'storage')
    _start_srv(tracker_collection, 'tracker_collection')
    _start_srv(scheduler, 'scheduler')

def handle_command_line_args():
    # TODO: This is bad. If we wand to use command line arguments we need to use
    # `optparse`.
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

    sender.fire('COLLECTOR.SERVICE_STARTED.SUCCESS',
                srv_name='backdoor')
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
        sender.fire('COLLECTOR.FAILURE',
                    error_details=traceback.format_exc())
        sys.exit(-1)

