import logging

from odoo import fields, models, api

from odoo.addons.generic_system_event import on_event

_logger = logging.getLogger(__name__)


class RequestRequest(models.Model):
    _inherit = 'request.request'

    weight = fields.Float(readonly=True)

    @property
    def _order(self):
        cls = type(self)
        date_order_direction = self.sudo().env[
            'ir.config_parameter'
        ].get_param(
            'generic_request_weight.request_sort_direction', 'DESC')
        cls._order = 'weight ASC, date_created %s' % date_order_direction
        return cls._order

    @api.model
    def _setup_complete(self):
        res = super()._setup_complete()

        cls = type(self)

        # Cleanup memoized `_order` property for request.
        cls._order = RequestRequest._order

        return res

    def _get_request_weight__sla(self):
        sla_states = [r.sla_state for r in self.sla_control_ids]
        if 'failed' in sla_states:
            sla_weight = 0.1
        elif 'warning' in sla_states:
            sla_weight = 0.5
        elif 'ok' in sla_states:
            sla_weight = 1.0
        else:
            sla_weight = 10.0

        return sla_weight

    def _get_request_weight__activity(self):
        if self.activity_state == 'overdue':
            activity_weight = 0.1
        elif self.activity_state == 'today':
            activity_weight = 0.5
        else:
            activity_weight = 1.0
        return activity_weight

    def _get_request_weight__priority(self):
        if self.priority == '5':
            priority_weight = 0.0
        elif self.priority == '4':
            priority_weight = 0.5
        elif self.priority == '3':
            priority_weight = 1.0
        elif self.priority == '2':
            priority_weight = 5.0
        elif self.priority == '1':
            priority_weight = 10.0
        else:
            priority_weight = 1.0
        return priority_weight

    def _get_request_weight__kanban_state(self):
        if self.kanban_state == 'normal':
            return 1.0
        if self.kanban_state == 'done':
            return 0.01
        if self.kanban_state == 'blocked':
            return 10.0
        return 1.0

    def _get_request_weight__service(self):
        if not self.service_id:
            return 1.0
        return self.service_id.weight

    def _get_request_weight__service_level(self):
        if not self.service_level_id:
            return 1.0
        return self.service_level_id.weight

    def _get_request_weight__category(self):
        if not self.category_id:
            return 1.0
        return self.category_id.weight

    @on_event(
        'sla_warning',
        'sla_failed',
        'mail-activity-new',
        'mail-activity-done',
        'mail-activity-delete',
        'mail-activity-changed',
        'priority-changed',
        'impact-changed',
        'urgency-changed',
        'kanban-state-changed',
        'service-changed',
        'service-level-changed',
        'stage-changed',
        'category-changed',
        'record-created'
    )
    def _trigger_recompute_request_weight(self, event):
        self._recompute_request_weight()

    def _recompute_request_weight(self):
        for record in self.sudo():
            record.weight = (
                record.type_id.weight *
                record.stage_id.weight *
                record._get_request_weight__category() *
                record._get_request_weight__service() *
                record._get_request_weight__service_level() *
                record._get_request_weight__priority() *
                record._get_request_weight__kanban_state() *
                record._get_request_weight__sla() *
                record._get_request_weight__activity()
            )
