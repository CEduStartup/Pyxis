from django.db import models
from django.contrib.auth.models import User


class TrackerModel(models.Model):
    """ Tracker model.
    """
    class Meta:
        db_table = 'tracker'
    class Admin:
        pass

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

   ACCESS_METHODS = (
       (1, u'HTTP'),
       (2, u'SOAP'),
   )
   DATA_TYPES = (
       (1, u'XML'),
       (2, u'CSV'),
       (3, u'JSON'),
       (4, u'HTML'),
   )
   tracker          = models.ForeignKey(TrackerModel)
   access_method    = models.SmallIntegerField(choices=ACCESS_METHODS, default=0)
   query            = models.CharField(max_length=60)
   data_type        = models.SmallIntegerField(choices=DATA_TYPES, default=0)

class ValueModel(models.Model):
   """ Value model.
   """
   class  Meta:
       db_table  = 'value'
   VALUE_TYPES = (
       (1, u'Integer'),
       (2, u'Float'),
   )

   data_source     = models.ForeignKey(DataSourceModel)
   name            = models.CharField(max_length=60)
   value_type      = models.SmallIntegerField(choices=VALUE_TYPES, default=1)
   extraction_rule = models.CharField(max_length=200)
