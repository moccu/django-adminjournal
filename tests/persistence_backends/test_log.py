import flexmock
import pytest

from adminjournal import entry
from adminjournal.persistence_backends.log import Backend


@pytest.mark.django_db
class TestLogBackend:

    def test_persist(self, admin_user):
        backend = Backend()
        item = entry.Entry(entry.Entry.ACTION_VIEW, admin_user, admin_user.__class__)
        flexmock(backend.logger).should_receive('log').once().with_args(
            int, str(item), extra={'entry': item})
        assert backend.persist(item)

    @pytest.mark.parametrize('logger,expected', [
        (None, 'adminjournal'),
        ('adminjournal', 'adminjournal'),
        ('foo', 'foo')
    ])
    def test_logger(self, logger, expected, admin_user, settings):
        if logger:
            settings.ADMINJOURNAL_BACKEND_LOG_LOGGER = logger

        backend = Backend()
        assert backend.logger.name == expected

    @pytest.mark.parametrize('level,expected', [(None, 20), ('INFO', 20), ('WARNING', 30)])
    def test_persist_loglevel(self, level, expected, admin_user, settings):
        if level:
            settings.ADMINJOURNAL_BACKEND_LOG_LEVEL = level

        backend = Backend()
        item = entry.Entry(entry.Entry.ACTION_VIEW, admin_user, admin_user.__class__)
        flexmock(backend.logger).should_receive(
            'log').once().with_args(expected, str, extra=dict)

        assert backend.persist(item)
