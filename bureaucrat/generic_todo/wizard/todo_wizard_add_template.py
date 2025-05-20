import logging

from odoo import models, fields, api, Command

_logger = logging.getLogger(__name__)


class TodoWizardAddTemplate(models.TransientModel):
    _name = 'todo.wizard.add.template'
    _description = 'TodoWizardAddTemplate'

    res_model = fields.Char(
        store=True, string="Related Model", readonly=True, index=True)
    res_id = fields.Many2oneReference(
        string='Related Document', index=True, readonly=True,
        model_field='res_model')
    todo_template_id = fields.Many2one(
        'generic.todo.template')

    todo_wizard_add_template_line_ids = fields.One2many(
        'todo.wizard.add.template.line', 'todo_wizard_add_template_id')
    rewrite_lines = fields.Boolean(
        default=False,
        help='Rewrite widget lines by lines of the selected template. '
             'By default, lines will be added sequentially '
             'from each selected template.')

    def _get_vals_tuple_todo(self):
        lines = self.todo_wizard_add_template_line_ids.filtered(
            lambda line: line.to_add)

        lines = lines.sorted()
        vals_list_tuples = []
        for line in lines:
            vals = (0, 0, line._get_vals_todo_line())
            vals_list_tuples.append(vals)
        return vals_list_tuples

    @api.onchange('todo_template_id')
    def _onchange_todo_template_id(self):
        self.ensure_one()
        if self.rewrite_lines:
            self.todo_wizard_add_template_line_ids = [
                Command.clear()]  # Clear existing lines
        max_seq = max(
            [0] +
            [li.sequence for li in self.todo_wizard_add_template_line_ids]
        )
        if self.todo_template_id:
            for line in self.todo_template_id._get_vals_lines():
                max_seq += 1
                line.update({'sequence': max_seq})
                self.todo_wizard_add_template_line_ids = [Command.create(line)]

    def do_add_todo_lines(self):
        self.ensure_one()
        object_model = self.env[self.res_model].browse(self.res_id)

        object_model.write({
            'generic_todo_ids': self._get_vals_tuple_todo()
        })

    def do_overwrite_todo_lines(self):
        """
            Deactivate all todos on the object model by setting active = False,
            and add new todos from the wizard lines.
        """
        self.ensure_one()
        object_model = self.env[self.res_model].browse(self.res_id)

        # Deactivating old todos on object
        object_model.generic_todo_ids.action_archive()

        object_model.write({
            'generic_todo_ids': self._get_vals_tuple_todo()
        })


class TodoWizardAddTemplateLine(models.TransientModel):
    _name = 'todo.wizard.add.template.line'
    _inherit = 'generic.todo.mixin.todo'
    _description = 'Todo Wizard Add Template Line'
    _order = 'sequence ASC, id ASC'

    name = fields.Char(required=True)
    todo_type_id = fields.Many2one(
        'generic.todo.type', string="Todo Type",
        required=True, index=True, ondelete='cascade', auto_join=True)
    sequence = fields.Integer(
        required=True, readonly=False,
        help="Gives the sequence order for Todo Template Line.")
    to_add = fields.Boolean(
        help='Apply this line to model', default=True, index=True)

    todo_wizard_add_template_id = fields.Many2one(
        'todo.wizard.add.template')

    todo_type_model_name = fields.Char(related='todo_type_id.model_id.model')

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

    def _get_vals_todo_line(self):
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
