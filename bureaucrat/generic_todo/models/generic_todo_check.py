import logging
from odoo import models, fields


_logger = logging.getLogger(__name__)


class GenericTodoCheck(models.Model):
    _name = 'generic.todo.check'
    _description = 'Generic Todo Check'
    _inherit = [
        'generic.todo.mixin.implementation'
    ]

    description = fields.Html(translate=False)

    todo_is_ready = fields.Boolean(readonly=True)

    def _action_generic_todo_completed(self):
        if self.generic_todo_id.state == 'new':
            self.generic_todo_id.state = 'done'
            self.todo_is_ready = True

    def _action_generic_todo_start(self):
        if self.generic_todo_id.state == 'done':
            self.generic_todo_id.state = 'new'
            self.todo_is_ready = False
