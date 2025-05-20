from datetime import datetime
from odoo import models, fields


class GenericTeamMember(models.Model):
    _inherit = 'generic.team.member'

    def _get_min_datetime(self):
        return datetime(1970, 1, 1, 0, 0, 0)

    assigned_request_count = fields.Integer(
        related="user_id.assigned_request_count",
        readonly=True, store=True,
        string="Assigned Requests Count")
    assigned_request_open_count = fields.Integer(
        related="user_id.assigned_request_open_count",
        readonly=True, store=True,
        string="Assigned Open Requests To User")
    assigned_request_closed_count = fields.Integer(
        related="user_id.assigned_request_closed_count",
        readonly=True, store=True,
        string="Assigned Closed Requests")

    last_assign_time = fields.Datetime(default=_get_min_datetime)
