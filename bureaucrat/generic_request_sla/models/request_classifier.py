from odoo import models, fields, api


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    send_mail_on_request_sla_warning_event = fields.Boolean(
        default=True)
    request_sla_warning_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        default=lambda self:
        self._default_request_sla_warning_mail_template_id(),
        domain=[('model', '=', 'request.request')],
        help='This template will be used to send an email '
             'to the SLA user on SLA warning event.')
    send_mail_on_request_sla_failed_event = fields.Boolean(
        default=True)
    request_sla_failed_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        default=lambda self:
        self._default_request_sla_failed_mail_template_id(),
        domain=[('model', '=', 'request.request')],
        help='This template will be used to send an email '
             'to the SLA user on SLA failed event.')

    @api.model
    def _default_request_sla_warning_mail_template_id(self):
        template = self.env.ref(
            'generic_request_sla.mail_template_default_request_sla_warning',
            raise_if_not_found=False)
        return template.id if template else None

    @api.model
    def _default_request_sla_failed_mail_template_id(self):
        template = self.env.ref(
            'generic_request_sla.mail_template_default_request_sla_failed',
            raise_if_not_found=False)
        return template.id if template else None
