from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from adminjournal.models import Entry


class Command(BaseCommand):
    help = 'Clear adminjournal entries older than the configured lifetime.'

    def handle(self, *args, **options):
        days = getattr(settings, 'ADMINJOURNAL_ENTRY_EXPIRY_DAYS', 365)

        deleted = Entry.objects.filter(
            timestamp__lt=timezone.now() - timedelta(days=days)).delete()

        self.stdout.write(
            'Operation successful. {0} entries deleted.'.format(deleted[0]))
