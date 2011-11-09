from django.core.management.base import BaseCommand
from webui.frontend.models import TrackerModel, DataSourceModel, ValueModel
from random import randint

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            base_url = args[0]
            number   = int(args[1])
        except (IndexError, ValueError):
            print 'Please specify base url number of trackers to insert, for example ./manage.py trackers_generate http://127.0.0.1:9999/ 10'
            return
        
        if base_url.endswith("/"):
            base_url = base_url[:-1] 
            
        for i in xrange(number):
            #50..500
            divider = 50 + 11 * i % 500
            url = "%s/generator/xml/sin/%d" % (base_url, divider)
            tracker = TrackerModel(user_id=1, 
                                   name = 'Test Tracker #%d' % (i+1,),
                                   status=0,
                                   refresh_interval=randint(30, 300)
                                  )
            tracker.save()
            data_source = DataSourceModel(tracker=tracker,
                                          access_method=1,
                                          query='{"URI":"%s"}' % (url,),
                                          data_type=1
                                         )
            data_source.save()
            value = ValueModel(data_source=data_source,
                               name='Sin %d' % (i+1,),
                               value_type=1,
                               extraction_rule='/data/temperature/city[@id="lviv"]/temperature/@val'
                              )
            value.save()
            print 'Added "%s" \ttracker with URL: %s' % (tracker.name, url)
        
