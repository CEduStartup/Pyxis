import gevent.monkey; gevent.monkey.patch_all()
import signal
import sys
import traceback

import config.collector as collector_config
import config.storage as storage_config

from config.init.trackers import sender
from gevent.backdoor import BackdoorServer
from Scheduler import Scheduler
from shared.events.Event import CollectorServiceStartedEvent, CollectorFailureEvent
from shared.signal import utils as signal_utils
from storage import storage_types
from TrackerCollection import TrackerCollection


def cb_sighup_handler(sig, stack_frame):
    """SIGHUP signal handler.
    Read trackers configuration from DB and add it to Scheduler.
    """
    tracker_collection.load_trackers()

# New signal handlers map.
_SIGNAL_HANDLERS = {
    signal.SIGHUP: {
        'handler': cb_sighup_handler,
        'keep_old_handler': False
    },
}

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

    signal_utils.install_signal_handlers(_SIGNAL_HANDLERS)

def _start_srv(service, name):
    """Helper function to start service.
    """
    service.start()
    sender.fire(CollectorServiceStartedEvent, srv_name=name)


def run():
    """Implement main logic.
    """
    _start_srv(storage, 'storage')
    _start_srv(scheduler, 'scheduler')
    _start_srv(tracker_collection, 'tracker_collection')

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

    sender.fire(CollectorServiceStartedEvent, srv_name='backdoor')
    ## Temporarily commented, because backdoor thread locks everything.
    #BackdoorServer((host, port)).serve_forever()


if __name__ == '__main__':
    handle_command_line_args()

    try:
        initialize()
        run()
        initialize_backdoor()
    except Exception:
        # Here we need to handle all errors which are not handled by any
        # component above.
        sender.fire(CollectorFailureEvent,
                    error_details=traceback.format_exc())
        sys.exit(-1)

    ## Temporary, until problem with backdoor is solved.
    while(1):
        gevent.sleep(0)
