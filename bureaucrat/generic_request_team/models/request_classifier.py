from odoo import models, fields, api


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    send_mail_on_request_team_assigned_event = fields.Boolean(
        default=True)
    request_team_assigned_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        default=lambda self:
        self._default_request_team_assigned_mail_template_id(),
        domain=[('model', '=', 'request.request')],
        help='This template will be used to send an email '
             'to the assigned team on request team assigned event.'
    )

    @api.model
    def _default_request_team_assigned_mail_template_id(self):
        template = self.env.ref(
            'generic_request_team.mail_template_default_request_team_assigned',
            raise_if_not_found=False)
        return template.id if template else None
