import logging
from odoo import models, fields, _
from odoo.addons.generic_mixin import post_create, post_write


_logger = logging.getLogger(__name__)


class GenericTodoServerAction(models.Model):
    _name = 'generic.todo.server.action'
    _description = 'Generic Todo Server Action'
    _inherit = [
        'generic.todo.mixin.implementation'
    ]

    description = fields.Html(translate=False)

    run_info = fields.Char(readonly=True)

    action_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Server Action',
        ondelete='restrict',
        required=False,
        domain=[('model_name', '=', 'generic.todo.server.action')],
        help="Execute a server action when this todo is executed.",
        tracking=True,
    )

    @post_create()
    @post_write('action_id')
    def _set_domain_server_action_button(self, changes):
        """
        Creating a dynamic domain for start to-do button ( server action )
        """
        self.is_not_show_start = not bool(self.action_id)

    @staticmethod
    def _get_action_notification(message):
        """
        Get a pop-up message when a server action is performed
        """
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Warning'),
                'type': 'warning',
                'message': _(message),
                'sticky': False,
            }
        }

    def _action_generic_todo_start(self):
        """
        Execute a server action when pressing the start button of the To Do
        """
        if not self.action_id:
            self.run_info = 'Empty'

            return self._get_action_notification(
                "You have not specified a server action.")

        if self.generic_todo_id.state == 'new':
            try:
                self.action_id.with_context(
                    active_id=self.id,
                    active_ids=[self.id],
                    active_model='generic.todo.server.action').run()

                self.generic_todo_id.state = 'done'
                self.run_info = 'Successfully'

                _logger.info('Action executed successfully for '
                             'record ID %s', self.id)

            except Exception as e:
                _logger.error('Error executing action '
                              'for record ID %s: %s', self.id, e)

                self.generic_todo_id.state = 'canceled'
                self.run_info = 'Failed'

                return self._get_action_notification(
                    "An error occurred while executing the action.")

        return True
