# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import flexmock
import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from adminjournal import persistence
from adminjournal.entry import Entry


@pytest.mark.django_db
class TestEntry:

    @pytest.fixture(autouse=True)
    def setup(self, admin_user):
        self.init_kwargs = {
            'action': Entry.ACTION_VIEW,
            'user': admin_user,
            'model': admin_user
        }

    def test_init_invalid_action(self):
        self.init_kwargs['action'] = 'foo'
        with pytest.raises(ValueError) as exc:
            Entry(**self.init_kwargs)
            assert 'Invalid `action' in str(exc.value)

    def test_init_override_timestamp(self):
        self.init_kwargs['timestamp'] = timezone.now() + timedelta(days=1)
        entry = Entry(**self.init_kwargs)
        assert entry.timestamp > timezone.now()

    def test_init_invalid_user(self):
        self.init_kwargs['user'] = ContentType.objects.first()
        with pytest.raises(ValueError) as exc:
            Entry(**self.init_kwargs)
            assert 'Invalid `user' in str(exc.value)

    def test_init_invalid_no_model_and_class(self):
        self.init_kwargs.pop('model')
        with pytest.raises(ValueError) as exc:
            Entry(**self.init_kwargs)
            assert 'Missing `model' in str(exc.value)

    def test_init_invalid_model_missmatch_class(self):
        self.init_kwargs['model_class'] = ContentType.objects.get(
            app_label='auth', model='group')

        with pytest.raises(ValueError) as exc:
            Entry(**self.init_kwargs)
            assert 'Model / model_class missmatch' in str(exc.value)

    def test_init_valid_model_instance(self, admin_user):
        entry = Entry(**self.init_kwargs)
        assert entry.timestamp is not None
        assert entry.user == admin_user
        assert entry.model == admin_user

    def test_init_valid_model_class(self):
        self.init_kwargs['model_class'] = self.init_kwargs['user'].__class__
        entry = Entry(**self.init_kwargs)
        assert entry.content_type == ContentType.objects.get(
            app_label='auth', model='user')

    def test_init_valid_model_class_ct(self):
        ct = ContentType.objects.get(app_label='auth', model='user')
        self.init_kwargs['model_class'] = ct
        entry = Entry(**self.init_kwargs)
        assert entry.content_type == ct

    def test_repr(self, admin_user):
        self.init_kwargs['timestamp'] = datetime(2018, 11, 9, 11, 0, 0, tzinfo=timezone.utc)
        entry = Entry(**self.init_kwargs)
        assert repr(entry) == (
            '<Entry 2018-11-09 11:00:00+00:00: '
            'VIEW by admin on auth.user.%s: n/a>'
        ) % admin_user.pk

    def test_str(self, admin_user):
        self.init_kwargs['timestamp'] = datetime(2018, 11, 9, 11, 0, 0, tzinfo=timezone.utc)
        self.init_kwargs['description'] = 'foo'
        entry = Entry(**self.init_kwargs)
        entry.user.username = u'ädmin'
        assert str(entry) == 'VIEW by ädmin on auth.user.%s: foo' % admin_user.pk

    def test_str_payload(self, admin_user):
        self.init_kwargs['timestamp'] = datetime(2018, 11, 9, 11, 0, 0, tzinfo=timezone.utc)
        self.init_kwargs['payload'] = {'foo': 'bar'}
        entry = Entry(**self.init_kwargs)
        assert str(entry) == "VIEW by admin on auth.user.%s: {'foo': 'bar'}" % admin_user.pk

    def test_user_repr(self, admin_user):
        entry = Entry(**self.init_kwargs)
        assert entry.user_repr == admin_user.username

    def test_content_type_repr(self):
        entry = Entry(**self.init_kwargs)
        assert entry.content_type_repr == 'auth.user'

    def test_object_id_no_model(self, admin_user):
        self.init_kwargs.pop('model')
        self.init_kwargs['model_class'] = admin_user.__class__
        entry = Entry(**self.init_kwargs)
        assert entry.object_id is None

    def test_object_id_with_model(self, admin_user):
        entry = Entry(**self.init_kwargs)
        assert entry.object_id == admin_user.pk

    def test_persist(self):
        entry = Entry(**self.init_kwargs)
        flexmock(persistence).should_receive('persist').once().with_args(entry)
        entry.persist()
