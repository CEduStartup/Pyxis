""" Tracker events definitions.
"""

from Event import BaseEvent


class TrackerEvent(BaseEvent):

    """ Base class for all tracker events.

    Don't invoke this event.
    """

    tracker_id = None


class TrackerSuccessEvent(TrackerEvent):

    """ Invoked when tracker succesfully grabbed data.
    """

    eid = 'TRACKER.SUCCESS'
    message = 'Tracker %s succesfully grabbed data.'


class TrackerFailureEvent(TrackerEvent):

    """ Base class for all tracker failures events.
    """


class TrackerParseErrorEvent(TrackerFailureEvent):

    """ Invoked when parser error occure during data grabbing.
    """

    eid = 'TRACKER.FAILURE.PARSE'
    message = ''


class TrackerWorkflowEvent(TrackerEvent):

    """ Base class for all non-failure events during data grabbing.
    """

