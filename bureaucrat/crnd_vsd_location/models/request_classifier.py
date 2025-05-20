from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    read_show_location = fields.Boolean(default=False)
    create_show_location = fields.Boolean(default=False)

    # @api.onchange('location_required')
    # def _onchange_location_required(self):
    #     if self.location_required:
    #         self.location_invisible = False
