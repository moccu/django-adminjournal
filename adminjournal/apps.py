from django.apps import AppConfig
from django.contrib import admin

from .monkeypatch import patch_admin_site


class AdminjournalConfig(AppConfig):
    name = 'adminjournal'

    def ready(self):
        """
        When loading the adminjournal app, we patch the Django admin site to
        ensure every model admin is hooked to the admin journal mixin.

        TODO: Decide if we enable patching by default.
        """
        patch_admin_site(admin.site)
