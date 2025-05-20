from odoo import models, fields


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    is_default_notification_on = fields.Selection(
        selection_add=[
            ('team_assigned', 'Team assigned'),
        ],
        ondelete={
            'team_assigned': 'cascade',
        },
    )
