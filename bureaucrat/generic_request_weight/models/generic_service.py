from odoo import models, fields, api, _

from odoo.addons.generic_mixin import post_write
from odoo.exceptions import ValidationError


class GenericService(models.Model):
    _inherit = 'generic.service'

    weight = fields.Float(default=1.0, required=True)

    @api.constrains('weight')
    def _check_weight(self):
        for service in self:
            if service.weight < 0:
                raise ValidationError(_('Weight must be greater than zero.'))

    @post_write('weight')
    def _recompute_request_weight(self, changes):
        self.env['request.request'].search(
            [('service_id', 'in', self.ids), ('closed', '=', False)]
        )._recompute_request_weight()
