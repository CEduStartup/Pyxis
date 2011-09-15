import gevent
import settings
import sys
import time

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

if '--monitor' in sys.argv:
    def monitor_qsize():
        print time.strftime('%H:%M:%S')
        print '\tScheduler:', scheduler.get_run_queue_size()
        print '\tStorage:  ', storage.get_store_queue_size()
        gevent.sleep(2)

    gevent.spawn(monitor_qsize)

# Main thread just refreshing config
while True:
    trackerCollection.trackerUpdater()

