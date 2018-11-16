from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from adminjournal.models import Entry


@pytest.mark.django_db
class TestClearAdminjournal:

    def test_register_perms_called(self):
        Entry.objects.create(
            action='VIEW', user_repr='admin', content_type_repr='auth.User',
            timestamp=timezone.now() - timedelta(days=366))
        remaining_entry = Entry.objects.create(
            action='VIEW', user_repr='admin', content_type_repr='auth.User')

        call_command('clearadminjournal')

        assert Entry.objects.get() == remaining_entry
