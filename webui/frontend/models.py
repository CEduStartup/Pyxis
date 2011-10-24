from django.db import models
from django.contrib.auth.models import User

from shared.trackers import DATA_TYPES, ACCESS_METHODS, VALUE_TYPES


def _make_pretty(collection):
    """Return a list with the structure compatible for Django `choice` option
    e.g.::

        ((el_id1, 'pretty_name1'), (el_id2, 'pretty_name2'), ...)

    :Parameters:
        - `collection`: a dictionary of the following structure: ::

            {
                `el_id`: {`el_pretty_name`: 'pretty', `el_internal_name`: 'name'},
                ...
            }
    """
    return ((k, v['pretty']) for k, v in collection.iteritems())


class TrackerModel(models.Model):
    """ Tracker model.
    """
    class Meta:
        db_table = 'tracker'
    class Admin:
        pass

    def __unicode__(self):
        return self.name

    user             = models.ForeignKey(User)
    name             = models.CharField(max_length=60)
    status           = models.PositiveIntegerField(default=0)
    refresh_interval = models.PositiveIntegerField(default=3600)
    last_modified    = models.DateTimeField(auto_now=True, auto_now_add=True)


class DataSourceModel(models.Model):
    """ Data Source model.
    """
    class  Meta:
        db_table  = 'datasource'

    def __unicode__(self):
        return self.query

    tracker          = models.ForeignKey(TrackerModel)
    access_method    = models.SmallIntegerField(
                          choices=_make_pretty(ACCESS_METHODS), default=0)
    query            = models.CharField(max_length=60)
    data_type        = models.SmallIntegerField(
                          choices=_make_pretty(DATA_TYPES), default=0)

class ValueModel(models.Model):
    """ Value model.
    """
    class  Meta:
        db_table  = 'value'

    def __unicode__(self):
        return self.name

    data_source     = models.ForeignKey(DataSourceModel)
    name            = models.CharField(max_length=60)
    value_type      = models.SmallIntegerField(
       choices=_make_pretty(VALUE_TYPES), default=1)
    extraction_rule = models.CharField(max_length=200)

