from datetime import timedelta

import pytest
from django.utils import timezone

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
        with pytest.raises(ValueError):
            Entry(**self.init_kwargs)

    def test_init_override_timestamp(self):
        self.init_kwargs['timestamp'] = timezone.now() + timedelta(days=1)
        entry = Entry(**self.init_kwargs)
        assert entry.timestamp > timezone.now()

    def test_init_invalid_user(self):
        pass

    def test_init_invalid_no_model_and_class(self):
        pass

    def test_init_invalid_model_missmatch_class(self):
        pass

    def test_init_valid_model_instance(self, admin_user):
        entry = Entry(**self.init_kwargs)
        assert entry.timestamp is not None
        assert entry.user == admin_user
        assert entry.model == admin_user

    def test_init_valid_model_class_str(self):
        pass

    def test_init_valid_model_class_ct(self):
        pass

    def test_repr(self):
        pass

    def test_str(self):
        pass

    def test_user_repr(self):
        pass

    def test_content_type_repr(self):
        pass

    def test_object_id_no_model(self):
        pass

    def test_object_id_with_model(self):
        pass

    def test_persist(self):
        pass
