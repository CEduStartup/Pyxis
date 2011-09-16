import gevent
import settings
import sys
import time

from gevent.backdoor import BackdoorServer
from Scheduler import Scheduler
from TrackerCollection import TrackerCollection
from storage import storage_types


storage_class = storage_types[settings.STORAGE_TYPE]
storage = storage_class(settings.STORAGE_HOST, settings.STORAGE_PORT,
                        settings.STORAGE_DB_NAME)
scheduler = Scheduler()
trackerCollection = TrackerCollection(scheduler, storage)

storage.start()
scheduler.start()

def handle_command_line_args():
    MONITOR = '--monitor'
    BACKD = '--backdoor'
    HELP = '--help'

    if MONITOR in sys.argv:
        def monitor_qsize():
            while True:
                print time.strftime('%H:%M:%S')
                print '\tScheduler:', scheduler.get_run_queue_size()
                print '\tStorage:  ', storage.get_store_queue_size()
                gevent.sleep(int(sys.argv[sys.argv.index(MONITOR) + 1]))

        gevent.spawn(monitor_qsize)

    if BACKD in sys.argv:
        def start_backdoor():
            BackdoorServer(('127.0.0.1', int(sys.argv[sys.argv.index(BACKD) + 1]))).serve_forever()
        gevent.spawn(start_backdoor)

    if HELP in sys.argv:
        print """\
Options:
--help - print this message without running app.
--monitor SECONDS - print scheduler and storage queue with SECONDS interval.
--backdoor PORT - start backdoor server listening to PORT on localhost.
"""
        exit()

handle_command_line_args()

# Main thread just refreshing config
while True:
    trackerCollection.trackerUpdater()

