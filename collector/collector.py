import gevent

from Scheduler import Scheduler
from TrackerCollection import TrackerCollection

scheduler = Scheduler()
trackerCollection = TrackerCollection(scheduler)

scheduler.start()

# Main thread just refreshing config
while True:
    trackerCollection.trackerUpdater()

