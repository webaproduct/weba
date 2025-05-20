from odoo import models, fields


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    is_default_notification_on = fields.Selection(
        selection_add=[
            ('sla_warning', 'SLA warning'),
            ('sla_failed', 'SLA failed'),
        ],
        ondelete={
            'sla_warning': 'cascade',
            'sla_failed': 'cascade'
        },
    )
