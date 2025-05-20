from odoo import models, fields


class MailMail(models.Model):
    _inherit = 'mail.mail'

    is_request_default_notification_mail = fields.Boolean(
        help='This mail is used as default notification for Request Event',
        default=False)
