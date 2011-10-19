from django.db import models
from django.contrib.auth.models import User


class TrackerModel(models.Model):
    """ Tracker model.
    """
    class Meta:
        db_table = 'tracker'

    user             = models.ForeignKey(User)
    name             = models.CharField(max_length=60)
    status           = models.PositiveIntegerField()
    refresh_interval = models.PositiveIntegerField()
    last_modified    = models.DateTimeField(auto_now=True, auto_now_add=True)


class DataTypeModel(models.Model):
   """ Data type model.
   """
   class  Meta:
       db_table  = 'datatype'

   name              = models.CharField(max_length=60)


class AccessMethodModel(models.Model):
   """ Access method model.
   """
   class  Meta:
       db_table  = 'accessmethod'

   name              = models.CharField(max_length=60)


class DataSourceModel(models.Model):
   """ Data Source model.
   """
   class  Meta:
       db_table  = 'datasource'

   tracker       = models.ForeignKey(TrackerModel)
   access_method = models.ForeignKey(AccessMethodModel)
   query            = models.CharField(max_length=60)
   data_type	    = models.ForeignKey(DataTypeModel)


class ValueTypeModel(models.Model):
   """ Value type model.
   """
   class  Meta:
       db_table  = 'valuetype'
   
   name              = models.CharField(max_length=60)


class ValueModel(models.Model):
   """ Value model.
   """
   class  Meta:
       db_table  = 'value'

   data_source     = models.ForeignKey(DataSourceModel)
   name              = models.CharField(max_length=60)
   value_type     = models.ForeignKey(ValueTypeModel)
   extraction_rule   = models.CharField(max_length=200)
