class BaseBackend(object):
    """
    Base backend to persist journal entries.

    Every backend must provide at least a `persist` method.
    """

    def __init__(self):
        pass

    def persist(self, entry):
        """
        The `persist` method is able to persist instances of `adminjournal.entry.Entry`
        classes. The method will return `True` or `False` to signal success.
        """
        raise NotImplementedError
