import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class GenericTodoMixinTodo(models.AbstractModel):
    _name = 'generic.todo.mixin.todo'
    _description = 'Generic Todo MixIn Todo'

    @staticmethod
    def _change_vals_for_todo_type(model_name, vals):
        """
        Additional method about check current fields
        """
        if model_name == 'generic.todo.server.action':
            vals['todo_list_template_id'] = False
        elif model_name == 'generic.todo.list.todo':
            vals['action_id'] = False
        else:
            vals['action_id'] = False
            vals['todo_list_template_id'] = False
        return vals

    @api.model
    def create(self, vals):
        """
        Check and clearing fields when create new line
        """
        if 'todo_type_id' in vals:
            todo_type = self.env['generic.todo.type'].browse(
                vals['todo_type_id'])
            model_name = todo_type.model_id.model
            vals = self._change_vals_for_todo_type(model_name, vals)
        return super(GenericTodoMixinTodo, self).create(vals)

    def write(self, vals):
        """
        Check and clearing fields when update new line
        """
        for record in self:
            todo_type = record.todo_type_id
            if 'todo_type_id' in vals:
                todo_type = self.env['generic.todo.type'].browse(
                    vals['todo_type_id'])
            model_name = todo_type.model_id.model
            vals = self._change_vals_for_todo_type(model_name, vals)
        return super(GenericTodoMixinTodo, self).write(vals)

    @api.onchange('action_id')
    def _onchange_acton_id(self):
        """
        Clear field if not the right type
        """
        if self.todo_type_model_name != 'generic.todo.server.action':
            self.action_id = False
            return

    @api.onchange('todo_list_template_id')
    def _onchange_todo_list_template_id(self):
        """
        Clear field if wrong type and limit nesting for to do list
        """
        if self.todo_type_model_name != 'generic.todo.list.todo':
            self.todo_list_template_id = False
            return None

        if not self.todo_list_template_id:
            return None

        for line in self.todo_list_template_id.todo_template_line_ids:
            if line.todo_type_model_name == 'generic.todo.list.todo':
                self.todo_list_template_id = False
                return {
                    'warning': {
                        'title': "Invalid Selection",
                        'message': "The selected task type does not allow "
                                   "using this todo list template. "
                                   "The field will be cleared.",
                    }
                }
        return None
