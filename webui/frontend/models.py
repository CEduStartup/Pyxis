from django.db.models import *
from django.contrib.auth.models import User

from shared.trackers import DATA_TYPES, ACCESS_METHODS, VALUE_TYPES
from shared.Utils import PERIOD_CHOICES, METHOD_CHOICES, TYPE_CHOICES


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

class ViewModel(Model):
    """ View model.
    """
    class Meta:
        db_table = 'view'
    class Admin:
        pass

    user             = ForeignKey(User, default=1)
    view_name        = CharField(max_length=60, null=False, blank=False)
    view_description = TextField(null=True, blank=True)
    start            = DateField(null=False, blank=False)
    end              = DateField(null=False, blank=False)
    periods          = CharField(choices=PERIOD_CHOICES, max_length=15,
                                 null=False, blank=False)
    types            = CharField(choices=TYPE_CHOICES, max_length=15,
                                 null=False, blank=False)
    trackers         = TextField(null=False, blank=False)

    def __unicode__(self):
        return '<ViewModel %s: %s>' % (self.id, self.view_name)

class TrackerModel(Model):
    """ Tracker model.
    """
    class Meta:
        db_table = 'tracker'
    class Admin:
        pass

    user             = ForeignKey(User)
    name             = CharField(max_length=60)
    status           = PositiveIntegerField(default=0)
    refresh_interval = PositiveIntegerField(default=3600)
    last_modified    = DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '<TrackerModel %s: %s>' % (self.id, self.name)

class DataSourceModel(Model):
    """ Data Source model.
    """
    class  Meta:
        db_table  = 'datasource'

    def __unicode__(self):
        return self.query

    tracker          = ForeignKey(TrackerModel)
    access_method    = SmallIntegerField(
                          choices=_make_pretty(ACCESS_METHODS), default=0)
    query            = TextField()
    data_type        = SmallIntegerField(
                          choices=_make_pretty(DATA_TYPES), default=0)

class ValueModel(Model):
    """ Value model.
    """
    class  Meta:
        db_table  = 'value'

    def __unicode__(self):
        return self.name

    data_source     = ForeignKey(DataSourceModel)
    name            = CharField(max_length=60)
    value_type      = SmallIntegerField(
       choices=_make_pretty(VALUE_TYPES), default=1)
    extraction_rule = CharField(max_length=200)

    def __unicode__(self):
        return '<ValueModel %s: %s>' % (self.id, self.name)

