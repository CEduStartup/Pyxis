from trackers import BaseTracker
from config import logger

class Tracker(BaseTracker):
    """ This is dummy tracker, which does nothing"""

    def grab_data(self):
        """ On grab_data call it just logs simple message. """
        logger.info('just simple message from tracker %s' % self.tracker_id)

        

