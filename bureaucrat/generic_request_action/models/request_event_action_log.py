from odoo import models, fields, api


class RequestEventActionLog(models.Model):
    _name = 'request.event.action.log'
    _order = 'date DESC'
    _description = "Request Event Action Log"
    _log_access = False

    date = fields.Datetime(
        required=True, index=True, readonly=True,
        default=fields.Datetime.now)
    request_id = fields.Many2one(
        comodel_name='request.request',
        index=True, required=True, readonly=True)
    action_id = fields.Many2one(
        comodel_name='request.event.action',
        required=True, readonly=True)
    event_id = fields.Many2one(
        comodel_name='request.event', readonly=True)
    event_type_id = fields.Many2one(
        comodel_name='generic.system.event.type',
        required=True, readonly=True)
    user_id = fields.Many2one(
        comodel_name='res.users', required=True, readonly=True)

    # Status/error info
    message = fields.Text(readonly=True)
    success = fields.Boolean(default=True, readonly=True, index=True)

    @api.depends('display_name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (f"{rec.date}: {rec.request_id.display_name} "
                                f"[{rec.action_id.display_name}]")
        return True
