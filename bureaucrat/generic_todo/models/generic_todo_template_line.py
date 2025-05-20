from odoo import fields, models, api


class GenericTodoTemplateLine(models.Model):
    _name = 'generic.todo.template.line'
    _inherit = 'generic.todo.mixin.todo'
    _description = 'Generic Todo Template Line'
    _order = 'sequence ASC, id ASC'

    name = fields.Char(index=True, required=True)

    todo_template_id = fields.Many2one(
        'generic.todo.template', index=True)
    todo_type_id = fields.Many2one(
        'generic.todo.type', string="Todo Type",
        required=True, index=True, ondelete='cascade', auto_join=True)
    # additional field for attrs invisible fields on xml
    todo_type_model_id = fields.Many2one(comodel_name='ir.model',
                                         related='todo_type_id.model_id')
    todo_type_model_name = fields.Char(related='todo_type_id.model_id.model')
    sequence = fields.Integer(
        default=5, index=True,
        help="Gives the sequence order for Todo Template Line.")

    action_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Server Action',
        ondelete='restrict',
        required=False,
        domain=[('model_name', '=', 'generic.todo.server.action')],
        help="Execute a server action when this todo is executed.",
        tracking=True,
    )

    todo_list_template_id = fields.Many2one(
        'generic.todo.template', index=True)

    @api.model
    def _add_missing_default_values(self, values):
        todo_template = values.get('res_model', False)
        todo_lines = self.search([
            ('todo_template_id', '=', todo_template)
        ])

        if todo_lines:
            values['sequence'] = max(s.sequence for s in todo_lines) + 1

        return super()._add_missing_default_values(values)

    def _get_vals_todo_template_line(self):
        self.ensure_one()
        vals = {
            'name': self.name,
            'todo_type_id': self.todo_type_id.id,
        }
        generic_todo_type_server_action_id = self.env.ref(
            'generic_todo.generic_todo_type_server_action').id
        generic_todo_type_list_todo_id = self.env.ref(
            'generic_todo.generic_todo_type_list_todo').id

        if (self.todo_type_id.id == generic_todo_type_server_action_id and
                self.action_id):
            vals.update({'action_id': self.action_id.id})
        if (self.todo_type_id.id == generic_todo_type_list_todo_id and
                self.todo_list_template_id):
            vals.update({
                'todo_list_template_id': self.todo_list_template_id.id})

        return vals
