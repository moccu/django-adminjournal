import flexmock

from adminjournal.persistence import get_persistence_backend, persist
from adminjournal.persistence_backends import db, log


class TestPersist:

    def test_default_backend(self):
        foo = object()
        flexmock(db.Backend).should_receive('persist').once().with_args(foo)
        persist(foo)

    def test_provided_backend(self):
        foo = object()
        flexmock(log.Backend).should_receive('persist').once().with_args(foo)
        persist(foo, 'adminjournal.persistence_backends.log.Backend')


class TestGetPersistenceBackend:

    def test_default(self):
        assert isinstance(get_persistence_backend(), db.Backend)

    def test_settings_override(self, settings):
        settings.ADMINJOURNAL_PERSISTENCE_BACKEND = (
            'adminjournal.persistence_backends.log.Backend')

        assert isinstance(get_persistence_backend(), log.Backend)

    def test_called_with_path(self, settings):
        assert isinstance(get_persistence_backend(
            'adminjournal.persistence_backends.log.Backend'), log.Backend)
