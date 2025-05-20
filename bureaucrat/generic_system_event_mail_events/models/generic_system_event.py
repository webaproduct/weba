from odoo import models, fields


class GenericSystemEvent(models.Model):
    _inherit = "generic.system.event"

    mail_message_id = fields.Many2one('mail.message', readonly=True)
    mail_subject = fields.Char(
        related='mail_message_id.subject', readonly=True)
    mail_body = fields.Html(
        related='mail_message_id.body', readonly=True)
    mail_activity_id = fields.Many2one('mail.activity', readonly=True)
    mail_activity_type_id = fields.Many2one(
        'mail.activity.type', readonly=True)
