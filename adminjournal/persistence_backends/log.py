import logging

from django.conf import settings

from .base import BaseBackend


class Backend(BaseBackend):
    """
    Simple backend that uses Python-logging to "persist" a given entry.

    The log backend has two settings:
        * ADMINJOURNAL_BACKEND_LOG_LOGGER: Name of the logger to use
        * ADMINJOURNAL_BACKEND_LOG_LEVEL: Valid logging level name to use
    """

    def __init__(self):
        self.logger = logging.getLogger(
            getattr(settings, 'ADMINJOURNAL_BACKEND_LOG_LOGGER', 'adminjournal'))

    def persist(self, entry):
        loglevel = getattr(settings, 'ADMINJOURNAL_BACKEND_LOG_LEVEL', 'INFO')
        self.logger.log(logging.getLevelName(loglevel), str(entry), extra={'entry': entry})
        return True
