from odoo import models, fields


class RequestDeadlineChangeReason(models.Model):
    _name = 'request.deadline.change.reason'
    _description = 'Request Deadline Change Reason'
    _rec_name = 'name'
    _inherit = [
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code'
    ]

    reason = fields.Text(required=True)
