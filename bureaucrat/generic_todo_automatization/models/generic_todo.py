from odoo import models, fields, api
from odoo.addons.generic_system_event import on_event


class GenericTodo(models.Model):
    _inherit = 'generic.todo'

    post_create_server_action = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Post create server Action',
        ondelete='restrict',
        required=False,
        help="Execute a server action just after create.",
    )
    pre_start_server_action = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Pre start server Action',
        ondelete='restrict',
        required=False,
        help="Execute a server action when todo in state 'In progress'.",
    )
    on_cancel_server_action = fields.Many2one(
        comodel_name='ir.actions.server',
        string='On cancel server Action',
        ondelete='restrict',
        required=False,
        help="Execute a server action when todo in state 'Cancel'.",
    )
    on_done_server_action = fields.Many2one(
        comodel_name='ir.actions.server',
        string='On done server Action',
        ondelete='restrict',
        required=False,
        help="Execute a server action when todo in state 'Done'.",
    )
    on_done_auto_start_next_todo = fields.Boolean(
        default=False,
        help='Autostart next by sequence todo in object.'
    )
    autostart_todo = fields.Boolean(
        default=False,
        help='Autostart todo just after create.'
    )

    @on_event(
        'generic-todo-state-changed',
        event_source='generic.todo')
    def _on_event_stage_changed_automatization(self, event):
        new_state = event['new_state']
        self._dispatch_automation_todo_state(new_state)

    def _dispatch_automation_todo_state(self, new_state):
        """Dispatch actions based on the new state of the TODOS."""
        if new_state == 'in_progress':
            self._run_pre_start_action()

        elif new_state == 'canceled':
            self._run_on_canceled_action()

        elif new_state == 'done':
            self._run_on_done_action()

    def _run_pre_start_action(self):
        """Run the pre-start server action if applicable."""
        if self.pre_start_server_action:
            self.pre_start_server_action.with_context(
                active_id=self.todo_implementation_res_id,
                active_ids=[self.todo_implementation_res_id],
                active_model=self.todo_implementation_model,
            ).run()

    def _run_on_canceled_action(self):
        if self.on_cancel_server_action:
            self.on_cancel_server_action.with_context(
                active_id=self.todo_implementation_res_id,
                active_ids=[self.todo_implementation_res_id],
                active_model=self.todo_implementation_model,
            ).run()

    def _run_on_done_action(self):
        """Run the on-done server action
            and optionally start the next TODOS."""
        if self.on_done_server_action:
            self.on_done_server_action.with_context(
                active_id=self.todo_implementation_res_id,
                active_ids=[self.todo_implementation_res_id],
                active_model=self.todo_implementation_model,
            ).run()

        if self.on_done_auto_start_next_todo and self.todo_object:
            self._do_start_todo_object_next_todo(self.todo_object)

    def _do_start_todo_object_next_todo(self, todo_object):
        """Start the next TODOS item if it exists."""
        next_todo = self._get_todo_object_next_todo(todo_object)
        if next_todo:
            next_todo.todo_implementation._action_generic_todo_start()

    def _get_todo_object_next_todo(self, todo_object):
        """Retrieve the next TODOS item based on the sequence."""
        todos = todo_object.generic_todo_ids
        sorted_todos = list(todos.sorted(key=lambda r: r.sequence))
        current_index = sorted_todos.index(self)
        next_todo = (
            sorted_todos[current_index + 1]
            if current_index + 1 < len(sorted_todos)
            else None
        )
        return next_todo

    def _get_todo_object_previous_todo(self, todo_object):
        """Retrieve the previous TODOS item based on the sequence."""
        if not todo_object or not todo_object.generic_todo_ids:
            return None
        todos = todo_object.generic_todo_ids
        sorted_todos = list(todos.sorted(key=lambda r: r.sequence))
        current_index = sorted_todos.index(self)
        previous_todo = (
            sorted_todos[current_index - 1]
            if current_index - 1 >= 0
            else None
        )
        return previous_todo

    def _can_autostart_on_done_auto_start_next_todo(self, previous_todo):
        '''
            Check can autostart todos, when 'on_done_auto_start_next_todo'
            flag is set on previous todos
        '''
        if not previous_todo:
            return False
        if not previous_todo.on_done_auto_start_next_todo:
            return False
        if not previous_todo.state == 'done':
            return False
        if self.state != 'new':
            return False
        return True

    @api.model
    def create(self, vals):
        record = super(GenericTodo, self).create(vals)
        if record.post_create_server_action:
            record.todo_implementation.post_create_server_action.with_context(
                active_id=record.todo_implementation_res_id,
                active_ids=[record.todo_implementation_res_id],
                active_model=record.todo_implementation_model,
            ).run()
        if record.autostart_todo:
            record.todo_implementation._action_generic_todo_start()
        # Find the previous TODOS, and if it is marked with
        # 'on_done_auto_start_next_todo' and its state is 'done',
        # automatically start the current TODOS.
        # This is necessary because todos with flag
        # 'on_done_auto_start_next_todo' may reach the 'done' state
        # during it's creation, before the next todos created.
        # As a result, the next TODOS cannot be started at this point.
        previous_todo = record._get_todo_object_previous_todo(
            record.todo_object)
        can_autostart = record._can_autostart_on_done_auto_start_next_todo(
            previous_todo)
        if can_autostart:
            record.todo_implementation._action_generic_todo_start()
        return record
