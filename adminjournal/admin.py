from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Entry


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    search_fields = ('user_repr',)
    list_display = (
        '__str__', 'action', 'content_type_repr', 'user_repr', 'object_id',
        'lazy_description'
    )
    list_filter = ('action', 'content_type__app_label', 'user_repr')
    date_hierarchy = 'timestamp'
    readonly_fields = (
        'timestamp', 'action', 'user', 'user_repr', 'content_type', 'content_type_repr',
        'object_id', 'object_repr', 'description', 'payload'
    )

    def has_add_permission(self, request, obj=None):
        """
        `has_add_permission` is overwritten to ensure no entries can be added.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        `has_delete_permission` is overwritten to ensure nobody can remove entries.
        """
        return False

    def lazy_description(self, obj):
        """
        Helper to return the human readable entry description. If no description
        is available, the payload will be returned.
        """
        return str(obj.description or obj.payload or 'n/a')
    lazy_description.short_description = _('Entry description')

    def object_repr(self, obj):
        """
        Helper to get the str-representation of the logged object.
        """
        if not obj.object_id or not obj.content_type:
            return 'n/a'

        try:
            instance = obj.content_type.get_object_for_this_type(pk=obj.object_id)

            if instance._meta.model in self.admin_site._registry:
                return mark_safe('<a href="{}">{}</a>'.format(
                    reverse('admin:%s_%s_change' % (
                        instance._meta.app_label,
                        instance._meta.model_name
                    ), args=(obj.object_id,)),
                    str(instance)
                ))

            return str(instance)
        except:
            return 'n/a'
    object_repr.short_description = _('Object')
