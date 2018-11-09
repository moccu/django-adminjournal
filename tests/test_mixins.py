from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from adminjournal.models import Entry


class GroupInline(admin.StackedInline):
    model = Group.permissions.through


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    inlines = [GroupInline]


class TestJournaledModelAdminMixin:

    def test_log_add(self, admin_client, admin_user):
        response = admin_client.get(reverse('admin:auth_permission_add'))
        assert response.status_code == 200
        assert Entry.objects.exists() is False

        response = admin_client.post(reverse('admin:auth_permission_add'), {
            'name': 'Foo perm',
            'content_type': ContentType.objects.get_by_natural_key('auth', 'user').pk,
            'codename': 'foo',
            'Group_permissions-TOTAL_FORMS': 3,
            'Group_permissions-INITIAL_FORMS': 0,
            'Group_permissions-MIN_NUM_FORMS': 0,
            'Group_permissions-MAX_NUM_FORMS': 0,
        })
        assert response.status_code == 302
        perms = Permission.objects.filter(codename='foo')
        assert len(perms) == 1

        entry = Entry.objects.get()
        assert entry.action == 'add'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id == str(perms[0].pk)
        assert entry.description == 'Added.'
        assert entry.payload == {'message': [{'added': {}}]}

    def test_log_change_get(self, admin_client, admin_user):
        obj = Permission.objects.create(
            name='Foo perm',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            codename='foo'
        )
        response = admin_client.get(
            reverse('admin:auth_permission_change', args=(obj.pk,)))
        assert response.status_code == 200

        entry = Entry.objects.get()
        assert entry.action == 'view'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id == str(obj.pk)
        assert entry.description == 'Object viewed.'
        assert entry.payload == {}

    def test_log_change_post_no_change(self, admin_client, admin_user):
        obj = Permission.objects.create(
            name='Foo perm',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            codename='foo'
        )
        response = admin_client.post(
            reverse('admin:auth_permission_change', args=(obj.pk,)),
            {
                'name': obj.name,
                'content_type': obj.content_type_id,
                'codename': obj.codename,
                'Group_permissions-TOTAL_FORMS': 3,
                'Group_permissions-INITIAL_FORMS': 0,
                'Group_permissions-MIN_NUM_FORMS': 0,
                'Group_permissions-MAX_NUM_FORMS': 0,
            }
        )
        assert response.status_code == 302

        entry = Entry.objects.get()
        assert entry.action == 'change'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id == str(obj.pk)
        assert entry.description == 'No fields changed.'
        assert entry.payload == {'message': []}

    def test_log_change_post_change(self, admin_client, admin_user):
        obj = Permission.objects.create(
            name='Foo perm',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            codename='foo'
        )
        response = admin_client.post(
            reverse('admin:auth_permission_change', args=(obj.pk,)),
            {
                'name': obj.name,
                'content_type': obj.content_type_id,
                'codename': 'foo2',
                'Group_permissions-TOTAL_FORMS': 3,
                'Group_permissions-INITIAL_FORMS': 0,
                'Group_permissions-MIN_NUM_FORMS': 0,
                'Group_permissions-MAX_NUM_FORMS': 0,
            }
        )
        assert response.status_code == 302

        entry = Entry.objects.get()
        assert entry.action == 'change'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id == str(obj.pk)
        assert entry.description == 'Changed codename.'
        assert entry.payload == {'message': [{'changed': {'fields': ['codename']}}]}

    def test_log_delete(self, admin_client, admin_user):
        obj = Permission.objects.create(
            name='Foo perm',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            codename='foo'
        )
        response = admin_client.post(
            reverse('admin:auth_permission_delete', args=(obj.pk,)),
            {'protected': False}
        )
        assert response.status_code == 302

        entry = Entry.objects.get()
        assert entry.action == 'delete'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id == str(obj.pk)
        assert entry.description == 'Deleted "auth | user | Foo perm"'
        assert entry.payload == {}

    def test_log_change_post_inline_add(self, admin_client, admin_user):
        obj = Permission.objects.create(
            name='Foo perm',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            codename='foo'
        )
        group = Group.objects.create(name='Baz')

        response = admin_client.post(
            reverse('admin:auth_permission_change', args=(obj.pk,)),
            {
                'name': obj.name,
                'content_type': obj.content_type_id,
                'codename': obj.codename,
                'Group_permissions-TOTAL_FORMS': 3,
                'Group_permissions-INITIAL_FORMS': 0,
                'Group_permissions-MIN_NUM_FORMS': 0,
                'Group_permissions-MAX_NUM_FORMS': 0,
                'Group_permissions-0-group': group.pk,
            }
        )
        assert response.status_code == 302

        rel_obj = group.permissions.through.objects.get()

        entry = Entry.objects.get()
        assert entry.action == 'change'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id == str(obj.pk)
        assert entry.description == (
            'Added group-permission relationship '
            '"Group_permissions object (%s)".'
        ) % rel_obj.pk
        assert entry.payload == {'message': [{'added': {
            'name': 'group-permission relationship',
            'object': 'Group_permissions object (%s)' % rel_obj.pk
        }}]}

    def test_log_change_post_inline_change(self, admin_client, admin_user):
        obj = Permission.objects.create(
            name='Foo perm',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            codename='foo'
        )
        group = Group.objects.create(name='Baz')
        group.permissions.add(obj)
        rel_obj = group.permissions.through.objects.get()

        group2 = Group.objects.create(name='Doe')

        response = admin_client.post(
            reverse('admin:auth_permission_change', args=(obj.pk,)),
            {
                'name': obj.name,
                'content_type': obj.content_type_id,
                'codename': obj.codename,
                'Group_permissions-TOTAL_FORMS': 3,
                'Group_permissions-INITIAL_FORMS': 1,
                'Group_permissions-MIN_NUM_FORMS': 0,
                'Group_permissions-MAX_NUM_FORMS': 0,
                'Group_permissions-0-id': rel_obj.pk,
                'Group_permissions-0-group': group2.pk,
            }
        )
        assert response.status_code == 302

        rel_obj = group2.permissions.through.objects.get()

        entry = Entry.objects.get()
        assert entry.action == 'change'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id == str(obj.pk)
        assert entry.description == (
            'Changed group for group-permission relationship '
            '"Group_permissions object (%s)".'
        ) % rel_obj.pk
        assert entry.payload == {'message': [{'changed': {
            'fields': ['group'],
            'name': 'group-permission relationship',
            'object': 'Group_permissions object (%s)' % rel_obj.pk
        }}]}

    def test_log_action(self, admin_client, admin_user):
        obj = Permission.objects.create(
            name='Foo perm',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            codename='foo'
        )

        response = admin_client.post(
            reverse('admin:auth_permission_changelist'),
            {
                'action': 'delete_selected',
                '_selected_action': [obj.pk],
            }
        )
        assert response.status_code == 200

        entry = Entry.objects.get()
        assert entry.action == 'view'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id is None
        assert entry.description == (
            'Action "Delete selected permissions" executed on 1 objects.')
        assert entry.payload == {
            'action': 'delete_selected',
            'selected_all': 0,
            'selected_ids': [str(obj.pk)]
        }

    def test_log_action_all(self, admin_client, admin_user):
        obj = Permission.objects.create(
            name='Foo perm',
            content_type=ContentType.objects.get_by_natural_key('auth', 'user'),
            codename='foo'
        )

        response = admin_client.post(
            reverse('admin:auth_permission_changelist'),
            {
                'action': 'delete_selected',
                '_selected_action': [obj.pk],
                'select_across': 1
            }
        )
        assert response.status_code == 200

        entry = Entry.objects.get()
        assert entry.action == 'view'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id is None
        assert entry.description == (
            'Action "Delete selected permissions" executed on all objects.')
        assert entry.payload == {
            'action': 'delete_selected',
            'selected_all': 1,
            'selected_ids': []
        }

    def test_log_changelist_invalid(self, admin_client, admin_user):
        response = admin_client.get(
            reverse('admin:auth_permission_changelist'),
            {'name__iinvalidname': 'oo'}

        )
        assert response.status_code == 302
        assert Entry.objects.exists() is False

    def test_log_changelist(self, admin_client, admin_user):
        response = admin_client.get(
            reverse('admin:auth_permission_changelist'))
        assert response.status_code == 200

        entry = Entry.objects.get()
        assert entry.action == 'view'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id is None
        assert entry.description == 'Changelist viewed.'
        assert entry.payload == {'filters': {}}

    def test_log_changelist_filtered(self, admin_client, admin_user):
        response = admin_client.get(
            reverse('admin:auth_permission_changelist'),
            {'name__icontains': 'oo'}
        )
        assert response.status_code == 200

        entry = Entry.objects.get()
        assert entry.action == 'view'
        assert entry.user == admin_user
        assert entry.content_type_repr == 'auth.permission'
        assert entry.object_id is None
        assert entry.description == 'Changelist viewed, filtered.'
        assert entry.payload == {'filters': {'name__icontains': 'oo'}}
