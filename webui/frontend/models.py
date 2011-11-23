import json
from utils import util
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

    REFRESH_INTERVAL_CHOICES = ((1800, '30 minutes'), (3600, '1 hour'), (7200, '2 hours'))

    user             = ForeignKey(User)
    name             = CharField(max_length=60, verbose_name='Tracker name:', help_text="""\
Tracker's name helps you identify your tracker among others. It's good idea to have name meaningful,
like <nobr>'Weather in my hometown'</nobr> or 'Currency exchange rate'.
""")
    status           = PositiveIntegerField(default=0)
    refresh_interval = PositiveIntegerField(default=3600, choices=REFRESH_INTERVAL_CHOICES,
                                            verbose_name='Polling interval:', help_text="""\
This is how often you want your data to be updated.
""")
    last_modified    = DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '<TrackerModel %s: %s>' % (self.id, self.name)

    def URI(self):
        """This is temporary, in future URI will not be a Tracker property."""
        return json.loads(self.datasourcemodel_set.get().query)['URI']

    def refresh_interval_pretty(self):
        """This is temporary, in future URI will not be a Tracker property."""
        return util.seconds_to_time(self.refresh_interval)


class DataSourceModel(Model):
    """ Data Source model.
    """
    class  Meta:
        db_table  = 'datasource'

    def __unicode__(self):
        return self.query

    tracker          = ForeignKey(TrackerModel)
    access_method    = SmallIntegerField(
                          choices=_make_pretty(ACCESS_METHODS), default=0,
                          verbose_name='Access method:', help_text="""\
Currently only access over the web (HTTP) is supported.""")
    query            = TextField()
    data_type        = SmallIntegerField(
                          choices=_make_pretty(DATA_TYPES), default=0,
                          verbose_name='Data type:', help_text="""\
Currently only XML data is supported.
""")


class ValueModel(Model):
    """ Value model.
    """
    class  Meta:
        db_table  = 'value'

    def __unicode__(self):
        return self.name

    data_source     = ForeignKey(DataSourceModel)
    name            = CharField(max_length=60, verbose_name='Value name:',
                                help_text="""\
Actually, this is what you'll see in your chart's Y axis label.""")
    value_type      = SmallIntegerField(
       choices=_make_pretty(VALUE_TYPES), default=1, verbose_name='Value type:',
       help_text="""\
Type of your value (integer or fractional).""")
    extraction_rule = CharField(max_length=200, verbose_name='Extraction rule:',
                                help_text="""\
Find the value you need in data below and click on it to get its path in data.""")

    def __unicode__(self):
        return '<ValueModel %s: %s>' % (self.id, self.name)

