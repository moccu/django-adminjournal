import importlib

from django.conf import settings


def persist(entry, backend=None):
    """
    The `persist` function is the abstract entrypoint to persist journal entries.
    The method receives a `adminjournal.entry.Entry` instance and an optional
    `backend` parameter to override the default persistence backend.

    The return value is either `True` of `False`, to signal if the entry was saved.
    """
    return get_persistence_backend(backend).persist(entry)


def get_persistence_backend(path=None):
    """
    Load a persistence backend and return a instance.
    If a path is provided, the backend is imported from that path.
    By default, ``adminjournal.persistence_backends.db.Backend`` is used.
    """
    path = path or getattr(
        settings,
        'ADMINJOURNAL_PERSISTENCE_BACKEND',
        'adminjournal.persistence_backends.db.Backend'
    )

    module_name, class_name = path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    backend_class = getattr(module, class_name)
    return backend_class()
