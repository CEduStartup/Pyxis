"""A management command which deletes all trackers."""

from django.core.management.base import NoArgsCommand

from frontend.models import TrackerModel


class Command(NoArgsCommand):
    help = "Delete all trackers."

    def handle_noargs(self, **options):
        TrackerModel.objects.delete_all_users()
