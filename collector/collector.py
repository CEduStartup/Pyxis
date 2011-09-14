import gevent
import settings


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

# Main thread just refreshing config
while True:
    trackerCollection.trackerUpdater()

