from odoo import models, fields


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    is_default_notification_on = fields.Selection([
        ('assign', 'Request assigned'),
        ('closed', 'Request closed'),
        ('reopened', 'Request reopened'),
        ('created', 'Request created')],
        help='This template will be used as default '
             'notification message for selected event')
