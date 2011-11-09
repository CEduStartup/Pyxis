from django.core.management.base import BaseCommand
from webui.frontend.models import TrackerModel, DataSourceModel, ValueModel
from random import randint

class Command(BaseCommand):
    def handle(self, *args, **options):
        trackers_count = TrackerModel.objects.count()
        TrackerModel.objects.all().delete()
        print "%d trackers were deleted" % trackers_count