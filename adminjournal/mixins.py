import json

from django.template.response import TemplateResponse

from .entry import Entry


class JournaledModelAdminMixin(object):
    """
    Mixin for ModelAdmin classes to issue journal entries on various actions
    via the model admin.

    Tracked actions:
        * View changelist (w/ and w/o filters)
        * View object change view
        * Change object
        * Add object
        * Delete object
        * Changelist actions (selected action and selected objects)
    """

    def log_to_adminjournal(self, action, user, message, model=None, payload=None):
        """
        The log_to_adminjournal method requires at least the action type and the
        issuing user together with a human readable message or a change_message-style
        list from Django's LogEntry.

        The method might use change_message-style lists to generate a human readable
        version of the data.

        If a change_message-style input is provided, the payload is ignored.

        If a str message is provided and the payload is a dictionary, the data is passed
        to the persistence layer.
        """

        # Django 1.9 returns a string, 1.10+ returns a list
        if isinstance(message, list):
            from django.contrib.admin.models import LogEntry
            payload = {'message': message}
            description = LogEntry(change_message=json.dumps(message)).get_change_message()
        else:
            payload = payload
            description = message

        Entry(
            action,
            user,
            model_class=self.model,
            model=model,
            description=description,
            payload=payload if isinstance(payload, dict) else {},
        ).persist()

    def log_addition(self, request, model, message):
        """
        In addition to the Django LogEntry, add another entry to the adminjournal.
        """
        self.log_to_adminjournal(Entry.ACTION_ADD, request.user, message, model)
        return super(JournaledModelAdminMixin, self).log_addition(request, model, message)

    def log_change(self, request, model, message):
        """
        In addition to the Django LogEntry, add another entry to the adminjournal.
        """
        self.log_to_adminjournal(Entry.ACTION_CHANGE, request.user, message, model)
        return super(JournaledModelAdminMixin, self).log_change(request, model, message)

    def log_deletion(self, request, model, object_repr):
        """
        In addition to the Django LogEntry, add another entry to the adminjournal.
        """
        self.log_to_adminjournal(
            Entry.ACTION_DELETE, request.user, 'Deleted "{}"'.format(object_repr), model)
        return super(JournaledModelAdminMixin, self).log_deletion(request, model, object_repr)

    def render_change_form(self, request, *args, **kwargs):
        """
        If a object change view is requested (GET request on change view),
        a ACTION_VIEW entry is generated to track read access to single objects.
        """
        if request.method == 'GET' and kwargs.get('change') and kwargs.get('obj'):
            self.log_to_adminjournal(
                Entry.ACTION_VIEW, request.user, 'Object viewed.', kwargs['obj'])

        return super(JournaledModelAdminMixin, self).render_change_form(
            request, *args, **kwargs)

    def response_action(self, request, queryset):
        """
        Actions on change lists are tracked too. To achieve this, this method
        parses the POST request and checks for various action fields to

        * Learn what action was triggered
        * What obejects are included in the action call
        * Are all objects involved or just some selected ones

        We don't know what the action does, therefore all actions are tracked
        as ACTION_VIEW.
        """

        try:
            action_index = int(request.POST.get('index', 0))
            action = request.POST.getlist('action')[action_index]

            selected_ids = request.POST.getlist('_selected_action')

            selected_all = request.POST.getlist('select_across')
            selected_all = int(selected_all[action_index]) if selected_all else 0
        except (ValueError, IndexError):
            # Invalidn action request, ignore for logging.
            return super(JournaledModelAdminMixin, self).response_action(request, queryset)

        action_name = dict(self.get_action_choices(request))[action]

        self.log_to_adminjournal(
            Entry.ACTION_VIEW,
            request.user,
            'Action "{}" executed on {} objects.'.format(
                action_name, 'all' if selected_all else len(selected_ids)),
            payload={
                'action': action,
                'selected_all': selected_all,
                'selected_ids': selected_ids if not selected_all else [],
            }
        )
        return super(JournaledModelAdminMixin, self).response_action(request, queryset)

    def changelist_view(self, request, *args, **kwargs):
        """
        GET requests on the changelist are tracked as ACTION_VIEW entries.
        The changelist view might also return redirects. This case is handled by
        ensuring that a proper TemplateResponse is available and the "cl" context
        (which is the ChangeList instance) is present.

        Parameters passed to the change list are tracked too. This allows to reconstruct
        the subset of objects a user viewed.
        """
        response = super(JournaledModelAdminMixin, self).changelist_view(
            request, *args, **kwargs)

        if isinstance(response, TemplateResponse) and 'cl' in response.context_data:
            filters = response.context_data['cl'].params
            self.log_to_adminjournal(
                Entry.ACTION_VIEW,
                request.user,
                'Changelist viewed{}'.format(', filtered.' if filters else '.'),
                payload={'filters': filters}
            )

        return response
