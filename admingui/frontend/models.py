from django.db import models
from django.contrib.auth.models import User

class Tracker(models.Model):
    """
    This class represents tracker storage in the database.
    """
    
    class Meta:
        db_table = 'trackers'
        
    STATUSES = (
        (0, u'Disabled'),
        (1, u'Enabled'),
    )
    
    RESOURCE_TYPES = (
        (1, u'XML'),
        (2, u'JSON'),
        (3, u'HTML'),
    )

    user         = models.ForeignKey(User)
    name         = models.CharField(max_length=60)
    url          = models.URLField(max_length=1024)
    interval     = models.PositiveIntegerField()
    res_type     = models.IntegerField(choices=RESOURCE_TYPES)
    values_count = models.PositiveIntegerField(default=0)
    values       = models.TextField()
    status       = models.SmallIntegerField(choices=STATUSES, default=0)
    
    def get_status(self):
        return dict(self.STATUSES)[self.status]
    
    def get_type(self):
        return dict(self.RESOURCE_TYPES)[self.res_type]
