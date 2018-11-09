from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model
from django.utils import timezone

from . import persistence


class Entry(object):
    """
    This class represents a journal entry and provides methods to get
    information about the action which was tracked.
    """
    ACTION_VIEW, ACTION_ADD, ACTION_CHANGE, ACTION_DELETE = ('view', 'add', 'change', 'delete')

    #: Point in time when the event happend.
    timestamp = None

    #: Dict-like object holding any other information related to the event.
    payload = None

    def __init__(
        self, action, user, model_class=None, model=None, description=None, timestamp=None,
        payload=None
    ):
        """
        Create a new entry instance.

        The constructor handles the provided data and does some basis validation.

        The parameters `action` and `user` are always required. It is possible to
        override the timestamp which used for that event.

        In addition, `model_class` and/or `model` needs to be provided.
        If both are given, the constructor will ensure that the `model_class`
        fits the `provided model`.

        It is allowed to provide one of the following as `model_class`:
            * Python class of a Django model
            * ContentType model instance
            * None (if none is provided, the model_class will be derived from the given model).

        You don't have to provide a `model` if you already have the `model_class` on hand.

        The parameter `description` is useful to provide a human-readable representation
        of what happened.
        """
        from django.contrib.contenttypes.models import ContentType

        self.timestamp = timestamp or timezone.now()

        if action not in (
            self.ACTION_VIEW,
            self.ACTION_ADD,
            self.ACTION_CHANGE,
            self.ACTION_DELETE
        ):
            raise ValueError('Invalid `action` provided: {}'.format(action))

        self.action = action

        if not isinstance(user, get_user_model()):
            raise ValueError('Invalid `user` provided: {} ({})'.format(user, user.__class__))

        self.user = user

        if not model_class and not model:
            raise ValueError('Missing `model_class` and/or `model`')

        if isinstance(model_class, ContentType):
            self.content_type = model_class
        else:
            self.content_type = get_content_type_for_model(model_class or model)

        class_from_ct = self.content_type.model_class()
        if model and not isinstance(model, class_from_ct):
            raise ValueError('Model / model_class missmatch: {} vs {}'.format(
                model, class_from_ct))

        self.model = model

        self.description = description or ''

        self.payload = payload or {}

    def __repr__(self):
        return '<Entry {}: {}>'.format(self.timestamp, str(self))

    def __str__(self):
        return '{} by {} on {}{}: {}'.format(
            self.action.upper(),
            self.user_repr,
            self.content_type_repr,
            '.{}'.format(self.object_id) if self.object_id else '',
            self.description or self.payload or 'n/a'
        )

    @property
    def user_repr(self):
        """
        Returns a human readable version of the user object.
        """
        return str(self.user)

    @property
    def content_type_repr(self):
        """
        Returns a human readable version of the content type object.
        """
        return '{}.{}'.format(self.content_type.app_label, self.content_type.model)

    @property
    def object_id(self):
        return self.model.pk if self.model else None

    def persist(self):
        """
        Triggers the persisting of the instance.
        """
        return persistence.persist(self)
