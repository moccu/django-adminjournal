from ..models import Entry
from .base import BaseBackend


class Backend(BaseBackend):
    """
    Database-backed persistence layer for journal entries.
    Uses adminjournal.Entry model to store entries to database.
    """

    def persist(self, entry):
        Entry.objects.create(
            timestamp=entry.timestamp,
            action=entry.action,
            user=entry.user,
            user_repr=entry.user_repr,
            content_type=entry.content_type,
            content_type_repr=entry.content_type_repr,
            object_id=entry.object_id,
            description=entry.description,
            payload=entry.payload
        )
        return True
