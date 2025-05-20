import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class GenericTodoSimple(models.Model):
    _name = 'generic.todo.simple'
    _description = 'Generic Todo Time'
    _inherit = [
        'generic.todo.mixin.implementation'
    ]

    description = fields.Html(translate=False)

    total_time_after_process = fields.Float(
        string="Total time",
        readonly=True,
        store=True,
        compute='_compute_total_time_after_process', )

    @api.depends('generic_todo_id.state')
    def _compute_total_time_after_process(self):
        for record in self:
            generic_todo_event_data_ids = self.env[
                'generic.todo.event.data'].search([
                    ('event_source_record_id', '=', record.generic_todo_id.id),
                    ('new_state', 'in',
                        ['in_progress', 'paused', 'done', 'canceled']),
                    ('event_code', '=', 'generic-todo-state-changed'),
                ])

            generic_todo_event_data_ids = sorted(generic_todo_event_data_ids,
                                                 key=lambda x: x['event_date'])

            start_time = None
            progress_time = 0

            for event in generic_todo_event_data_ids:

                if event['new_state'] == 'in_progress':
                    start_time = event['event_date']

                elif start_time and event['new_state'] in ['paused', 'done',
                                                           'canceled']:
                    end_time = event['event_date']

                    progress_time += (end_time - start_time).total_seconds()
                    start_time = None

            hours = int(progress_time // 3600)
            minutes = (progress_time % 3600) / 60
            progress_time_in_hours = hours + (minutes / 60)

            record.total_time_after_process = float(progress_time_in_hours)

            if record.list_todo_id:
                record.list_todo_id._update_total_time()
