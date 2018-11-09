# -*- coding: utf-8 -*-
from datetime import timedelta

import pytest
from django.utils import timezone

from adminjournal.models import Entry


@pytest.mark.django_db
class TestEntryModel:

    def test_str(self):
        obj = Entry.objects.create(
            action='VIEW', user_repr='admin', content_type_repr='auth.User')
        assert str(obj) == str(obj.timestamp)

    def test_ordering(self):
        obj1 = Entry.objects.create(
            action='VIEW', user_repr='admin', content_type_repr='auth.User',
            timestamp=timezone.now() - timedelta(minutes=1))
        obj2 = Entry.objects.create(
            action='VIEW', user_repr='admin', content_type_repr='auth.User',
            timestamp=timezone.now() - timedelta(minutes=2))
        assert list(Entry.objects.values_list('id', flat=True)) == [obj1.pk, obj2.pk]
