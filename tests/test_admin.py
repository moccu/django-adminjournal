import pytest
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from adminjournal.models import Entry


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


@pytest.mark.django_db
class TestEntryAdmin:

    def setup(self):
        self.modeladmin = admin.site._registry[Entry]

    def test_no_add_permission(self, admin_client):
        assert admin_client.get(
            reverse('admin:adminjournal_entry_add')).status_code == 403

    def test_no_delete_permission(self, admin_client):
        obj = Entry.objects.create(
            action='VIEW', user_repr='admin', content_type_repr='auth.User')
        assert admin_client.get(
            reverse('admin:adminjournal_entry_delete', args=(obj.pk,))).status_code == 403

    def test_lazy_description(self):
        obj = Entry.objects.create(
            action='VIEW',
            user_repr='admin',
            content_type_repr='auth.User',
            description='foo',
            payload={'foo': 'bar'}
        )
        assert self.modeladmin.lazy_description(obj) == 'foo'

    def test_lazy_description_payload(self):
        obj = Entry.objects.create(
            action='VIEW',
            user_repr='admin',
            content_type_repr='auth.User',
            payload={'foo': 'bar'}
        )
        assert self.modeladmin.lazy_description(obj) == "{'foo': 'bar'}"

    def test_lazy_description_no_data(self):
        obj = Entry.objects.create(
            action='VIEW',
            user_repr='admin',
            content_type_repr='auth.User',
        )
        assert self.modeladmin.lazy_description(obj) == 'n/a'

    def test_object_repr_no_object(self):
        obj = Entry.objects.create(
            action='VIEW',
            user_repr='admin',
            content_type_repr='auth.User',
        )
        assert self.modeladmin.object_repr(obj) == 'n/a'

    def test_object_repr_no_ct(self):
        obj = Entry.objects.create(
            action='VIEW',
            user_repr='admin',
            content_type_repr='auth.User',
            object_id=23
        )
        assert self.modeladmin.object_repr(obj) == 'n/a'

    def test_object_repr_object_not_found(self):
        obj = Entry.objects.create(
            action='VIEW',
            user_repr='admin',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            content_type_repr='auth.User',
            object_id=23
        )
        assert self.modeladmin.object_repr(obj) == 'n/a'

    def test_object_repr_no_modeladmin(self):
        ct = ContentType.objects.get_by_natural_key('contenttypes', 'contenttype')
        obj = Entry.objects.create(
            action='VIEW',
            user_repr='admin',
            content_type=ct,
            content_type_repr='contenttypes.ContentType',
            object_id=ct.pk
        )
        assert self.modeladmin.object_repr(obj) == 'content type'

    def test_object_repr_linked(self, admin_user):
        obj = Entry.objects.create(
            action='VIEW',
            user_repr='admin',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            content_type_repr='auth.User',
            object_id=admin_user.pk
        )
        assert self.modeladmin.object_repr(obj) == (
            '<a href="/admin/auth/user/%s/change/">admin</a>' % admin_user.pk)
