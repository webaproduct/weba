import logging
from odoo import models, fields


_logger = logging.getLogger(__name__)


class GenericTodoListTodo(models.Model):
    _name = 'generic.todo.list.todo'
    _description = 'Generic Todo List Todo'
    _inherit = [
        'generic.todo.mixin.implementation'
    ]

    description = fields.Html(translate=False)

    generic_todo_ids = fields.One2many(
        'generic.todo', 'list_todo_id',
        string='Todos',
    )

    total_time = fields.Float(
        readonly=True,
        store=True, )

    def _update_state(self):
        """
        Setting the state depending on the state of tasks inside
        """
        for record in self:
            todos_states = {todo.state for todo in record.generic_todo_ids}

            if todos_states == {'new'}:
                record.generic_todo_id.state = 'new'
            elif todos_states == {'done'}:
                record.generic_todo_id.state = 'done'
            else:
                record.generic_todo_id.state = 'in_progress'

    def _update_total_time(self):
        for record in self:
            total_time = sum(
                todo.todo_implementation.total_time_after_process for todo in
                record.generic_todo_ids if
                hasattr(todo.todo_implementation, 'total_time_after_process'))
            record.total_time = total_time
