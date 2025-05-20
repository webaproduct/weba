from odoo import models, fields


class RequestEvent(models.Model):
    _inherit = 'request.event'

    deadline_change_reason_id = fields.Many2one(
        'request.deadline.change.reason', string='Reason')
    deadline_change_comment = fields.Text(string='Comment')
