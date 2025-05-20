from odoo import fields, models


class GenericTodoTemplateLine(models.Model):
    _inherit = 'generic.todo.template.line'

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
        help="Autostart todo just after creation",
    )

    def _get_vals_todo_template_line(self):
        vals = super(
            GenericTodoTemplateLine, self)._get_vals_todo_template_line()
        vals.update({
            'post_create_server_action': self.post_create_server_action.id,
            'pre_start_server_action': self.pre_start_server_action.id,
            'on_cancel_server_action': self.on_cancel_server_action.id,
            'on_done_server_action': self.on_done_server_action.id,
            'on_done_auto_start_next_todo': self.on_done_auto_start_next_todo,
            'autostart_todo': self.autostart_todo,
        })
        return vals
