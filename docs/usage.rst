Usage
=====

After adding ``adminjournal`` to ``INSTALLED_APPS``, the journal is activated for
all model admins added to Django's default AdminSite (``django.contrib.admin.site``).

Cleanup
-------

Journal entries can be deleted automatically after a given amount of time (see
configuration option ``ADMINJOURNAL_ENTRY_EXPIRY_DAYS``). To do so, run the
``clearadminjournal`` regulary using a cron daemon or some other trigger tool.

If you use uwsgi, you might even us the built in cron helper::

    [uwsgi]
    # ...

    # Django session cleanup
    cron = 30 4 -1 -1 -1 django-admin clearsessions

    # Adminjournal cleanup
    cron = 15 4 -1 -1 -1 django-admin clearadminjournal

This would run the cleanup command every day at 4:15 am.
