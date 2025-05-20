from odoo import fields, models, api, _

from odoo.addons.generic_mixin import post_write
from odoo.exceptions import ValidationError


class RequestStage(models.Model):
    _inherit = 'request.stage'

    weight = fields.Float(default=1.0, required=True)

    @api.constrains('weight')
    def _check_weight(self):
        for stage in self:
            if stage.weight < 0:
                raise ValidationError(_('Weight must be greater than zero.'))

    @post_write('weight')
    def _recompute_request_weight(self, changes):
        self.env['request.request'].search(
            [('stage_id', 'in', self.ids), ('closed', '=', False)]
        )._recompute_request_weight()
