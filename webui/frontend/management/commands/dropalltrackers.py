"""A management command which deletes all trackers."""

from django.core.management.base import NoArgsCommand

from frontend.models import TrackerModel
from shared.services.services_api import mongo_storage_api


class Command(NoArgsCommand):
    help = "Delete all trackers."

    def handle_noargs(self, **options):
        for tracker in TrackerModel.objects.all():
            tracker.delete()

        mongo_storage_api().clear_db()
