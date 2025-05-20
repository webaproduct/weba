import logging
from odoo import models, fields, api
from odoo.osv import expression
from odoo.addons.generic_system_event import on_event
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m

_logger = logging.getLogger(__name__)


class RequestRequest(models.Model):
    _inherit = "request.request"

    event_action_log_ids = fields.One2many(
        'request.event.action.log', 'request_id', readonly=True)
    event_action_log_count = fields.Integer(
        readonly=True,
        compute='_compute_event_action_log_count',
        compute_sudo=True)

    @api.depends('event_action_log_ids')
    def _compute_event_action_log_count(self):
        mapped_data = read_counts_for_o2m(
            records=self,
            field_name='event_action_log_ids', sudo=True)
        for record in self:
            record.event_action_log_count = mapped_data.get(record.id, 0)

    @on_event('*')
    def _on_any_event__run_event_actions(self, event):
        domain = expression.AND([
            [('event_type_ids.id', '=', event.event_type_id.id)],
            expression.OR([
                [('request_type_id', '=', self.sudo().type_id.id)],
                [('request_type_id', '=', False)],
            ]),
        ])
        if event.route_id:
            domain = expression.AND([
                domain,
                expression.OR([
                    [('route_id', '=', False)],
                    [('route_id', '=', event.route_id.id)],
                ]),
            ])

        actions = self.env['request.event.action'].sudo().search(domain)
        # Run actions in original env
        self.env['request.event.action'].browse(actions.ids).with_context(
            request_event_ctx=event.get_context(),
            request_event=event,
        ).run(self, event)

    def action_show_action_log(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_request_action'
            '.action_request_event_action_logs',
            domain=[('request_id', '=', self.id)],
            context={'search_default_filter_failed': True}
        )
