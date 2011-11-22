"""A management command which deletes all accounts except superuser account."""

from django.core.management.base import NoArgsCommand

from registration.models import RegistrationProfile


class Command(NoArgsCommand):
    help = "Delete all users except superuser."

    def handle_noargs(self, **options):
        RegistrationProfile.objects.delete_all_users()
