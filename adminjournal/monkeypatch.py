import types

from django.conf import settings
from django.contrib import admin
from django.db.models.base import ModelBase

from .mixins import JournaledModelAdminMixin


def patch_admin_site(site):
    """
    This helper patches the default Django admin site to ensure the
    JournaledModelAdminMixin is added to the model admins.

    After patching the admin site, this helper checks all already registered
    model admins to be adminjournal enabled.
    """

    # Check/set a marker that we already patched this admin site.
    if hasattr(site, '_adminjournal_patched'):
        return
    site._adminjournal_patched = True

    # Remember original register method.
    vender_site_register = site.register

    def adminjournal_site_register(self, model_or_iterable, admin_class=None, **options):
        """
        Patched site.register that injects the JournaledModelAdminMixin if not present.
        """

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]

        if not admin_class:
            admin_class = admin.ModelAdmin

        whitelisted_models = getattr(settings, 'ADMINJOURNAL_MODEL_WHITELIST', ())
        for model in model_or_iterable:
            if (
                whitelisted_models == '__all__' or
                model._meta.label in whitelisted_models
            ) and not hasattr(admin_class, 'log_to_adminjournal'):
                # Mixin not present, create new class and add the mixin.
                patched_admin_class = type(
                    admin_class.__name__,
                    (JournaledModelAdminMixin, admin_class),
                    {}
                )
            else:
                patched_admin_class = admin_class

            vender_site_register([model], admin_class=patched_admin_class, **options)

    # Apply the new function as method to site instance.
    site.register = types.MethodType(adminjournal_site_register, site)

    # Check already registered model admins for adminjournal mixin.
    for model, admin_class in site._registry.items():
        if not hasattr(admin_class, 'log_to_adminjournal'):
            # Mixin missing, re-register.
            site.unregister(model)
            site.register(model, admin_class.__class__)
