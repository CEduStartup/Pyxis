from shared.trackers.datasources.HTTP import DatasourceHTTP
from shared.trackers.datasources.Errors import UnknownDatasourceError
from shared.trackers import HTTP_ACCESS_METHOD

def get_datasource(settings_dict):
    """Factory function, which returns concrete datasource object by source.

    :Parameters:
        - `access_method`: `dict` with datasource settings. It must contains
          `access_method` key with string value i.e.: SOAP, HTTP, XMLRPC, etc.

    :Return:
        - datasource class instance suitable for the given `access_method`.
    """
    access_method = settings_dict['access_method']
    if access_method in (HTTP_ACCESS_METHOD, ):
        return DatasourceHTTP(settings_dict)
    # TODO: add another types.
    else:
        raise UnknownDatasourceError('Datasource not found for access method'\
                 '"%s"' % (access_method,))