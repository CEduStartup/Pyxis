"""Contains all error classes for datasources.
"""

class BaseError(Exception):
 
    """ Base error.
    """

class BaseGrabError(BaseException):
    
    """ Base error for all grab exceptions. 
    """

class UnknownDatasourceError(BaseGrabError):

    """ Used when inable to determine datasource by source. 
    """

class ResponseGeventTimeout(BaseGrabError):
    
    """ Exception, generated on gevent timeout.
    """

class ResponseHTTPError(BaseGrabError):
    
    """ Wrapper for HTTPError. """

    def __init__(self, e, *args, **kwargs):
        BaseGrabError.__init__(self, *args, **kwargs)

class ResponseURLError(BaseGrabError):
    
    """ Wrapper for URLError. """

    def __init__(self, e, *args, **kwargs):
        BaseGrabError.__init__(self, *args, **kwargs)
