Installation
============

* Install with pip::

    pip install django-adminjournal


* Your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        # ...
        'adminjournal',
    )


Configuration options
---------------------

* ``ADMINJOURNAL_PERSISTENCE_BACKEND`` defines the backend that is used to
  store/persist the journal entries. Default is a database backend.
* ``ADMINJOURNAL_MODEL_WHITELIST`` defines the models to automatically activate
  the ModelAdmin mixin. The settings should be a list of Django models
  (e.g. ``auth.User``) or the string ``'__all__'`` to activate the admin journal
  for all models.
* ``ADMINJOURNAL_ENTRY_EXPIRY_DAYS`` defines the number of days after which the
  journal entries are deleted when calling the management command
  ``clearadminjournal``. The default is ``365`` days.
