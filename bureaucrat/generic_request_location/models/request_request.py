from odoo import models, fields, api


class RequestRequest(models.Model):
    _inherit = 'request.request'

    generic_location_id = fields.Many2one(
        'generic.location', 'Location', index=True, ondelete='restrict')

    location_required = fields.Boolean(
        related='classifier_id.location_required', readonly=True)
    location_invisible = fields.Boolean(
        related='classifier_id.location_invisible', readonly=True)

    @api.onchange('generic_location_id', 'partner_id')
    def _onchange_location_partner_update_partner(self):
        for record in self:
            if not record.partner_id and record.generic_location_id.partner_id:
                record.partner_id = record.generic_location_id.partner_id
