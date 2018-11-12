from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Entry(models.Model):
    timestamp = models.DateTimeField(_('Timestamp'), default=timezone.now)
    action = models.CharField(_('Action of entry'), max_length=16)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('User'),
        on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    user_repr = models.CharField(_('User (repr)'), max_length=255)

    content_type = models.ForeignKey(
        'contenttypes.ContentType', verbose_name=_('Content type'),
        on_delete=models.SET_NULL, blank=True, null=True, related_name='+')
    content_type_repr = models.CharField(_('Content type (repr)'), max_length=255)

    object_id = models.TextField(_('Object ID'), blank=True, null=True)

    description = models.TextField(_('Entry description'), blank=True)

    payload = JSONField(_('Payload'), blank=True, null=True)

    class Meta:
        verbose_name = _('Journal entry')
        verbose_name_plural = _('Journal entries')
        ordering = ('-timestamp',)

    def __str__(self):
        return str(self.timestamp)
