from django.apps import AppConfig
from django.conf import settings
from django.contrib import admin

from .monkeypatch import patch_admin_site


class AdminjournalConfig(AppConfig):
    name = 'adminjournal'

    def ready(self):
        """
        When loading the adminjournal app, we patch the Django admin site to
        ensure every model admin is hooked to the admin journal mixin if the
        setting ``ADMINJOURNAL_PATCH_ADMINSITE`` is set to True (default).
        """
        if getattr(settings, 'ADMINJOURNAL_PATCH_ADMINSITE', True):
            patch_admin_site(admin.site)
