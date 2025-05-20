from odoo import fields, models
from .request_request import RequestRequest


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    request_date_related_sort_direction = fields.Selection(
        config_parameter='generic_request_weight.request_sort_direction',
        selection=[
            ('ASC', 'Ascending'),
            ('DESC', 'Descending')],
        default='DESC', string='Request Sorting: Date Order',
        help='Preferred Request date sort order', required=True)

    def set_values(self):
        # Clear cached property _order when settings changes
        result = super(ResConfigSettings, self).set_values()
        req_cls = type(self.env['request.request'])
        req_cls._order = RequestRequest._order
        return result
