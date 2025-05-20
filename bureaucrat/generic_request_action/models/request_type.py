from odoo import models, fields, api
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m


class RequestType(models.Model):
    _inherit = "request.type"

    action_ids = fields.One2many(
        'request.event.action', 'request_type_id', 'Actions')
    action_count = fields.Integer(
        compute='_compute_action_count', readonly=True)

    @api.depends('action_ids')
    def _compute_action_count(self):
        mapped_data = read_counts_for_o2m(
            records=self,
            field_name='action_ids')
        for record in self:
            record.action_count = mapped_data.get(record.id, 0)

    def copy_request_data(self, dest_type):
        """ Copy request-specific data from self type to dest type

            Returns dictionary with cache, filled during copy.
            This way, it will be possible to use this cache in super overrides
            in other modules
        """
        cache = super().copy_request_data(dest_type=dest_type)
        cache['action_map'] = {
            act: act.copy({
                'request_type_id': dest_type.id,
                'route_id': (
                    cache['route_map'][act.route_id].id
                    if act.route_id and act.route_id in cache['route_map']
                    else False),
            })
            for act in self.action_ids
        }

        return cache

    def action_show_request_actions(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_request_action.action_request_event_actions',
            domain=[('request_type_id', '=', self.id)],
            context={
                'default_request_type_id': self.id,
            })
