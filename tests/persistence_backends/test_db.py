import pytest

from adminjournal import entry, models
from adminjournal.persistence_backends.db import Backend


@pytest.mark.django_db
class TestDbBackend:

    def test_persist(self, admin_user):
        item = entry.Entry(entry.Entry.ACTION_VIEW, admin_user, models.Entry)
        assert Backend().persist(item)

        obj = models.Entry.objects.get()
        assert obj.action == entry.Entry.ACTION_VIEW
        assert obj.user == admin_user
