from odoo import models, fields, api, _
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m
from odoo.addons.generic_mixin import post_write, post_create
from odoo.addons.generic_system_event import on_event
from markupsafe import Markup


class RequestRequest(models.Model):
    _inherit = 'request.request'

    # This field is used to make 'deadline_date' on request form readonly
    # after the first deadline was set up.
    # It becomes 'True' on postwrite/postcreate if deadline was set. After
    # this, we can change deadline date only via wizard (if stricted
    # deadline used).
    deadline_set = fields.Boolean(
        default=False,
        readonly=True)
    deadline_last_change_reason_id = fields.Many2one(
        'request.deadline.change.reason',
        readonly=True,
        string="Deadline change reason",
        help="The last changing deadline reason")
    deadline_last_change_comment = fields.Text(
        readonly=True,
        string="Deadline change comment",
        help="The last changing deadline comment")
    deadline_change_events_count = fields.Integer(
        'Deadline change events',
        compute='_compute_deadline_change_events_count',
        readonly=True)
    strict_deadline = fields.Boolean(
        related='type_id.use_strict_deadline',
        readonly=True)
    deadline_overdue = fields.Float(default=0)

    @api.depends('request_event_ids')
    def _compute_deadline_change_events_count(self):
        mapped_data = read_counts_for_o2m(
            records=self,
            field_name='request_event_ids',
            domain=[('event_code', '=', 'deadline-changed')])
        for record in self:
            record.deadline_change_events_count = mapped_data.get(record.id, 0)

    # The following method
    # is needed here to set deadline once on request form via standard way.
    # Later, the field can be changed only via wizard
    # indicating the reason for the change.
    # TODO: May be have reason get standard deadline changing possibility again
    #  when deadline was dropped to False via wizard?
    @post_create('deadline_date')
    @post_write('deadline_date')
    def _after_deadline_changed_update_deadline_set(self, changes):
        if changes['deadline_date'].new_val:
            self.deadline_set = True

    def trigger_event(self, event_type_code, event_data_vals=None):
        if event_type_code == 'deadline-changed' \
                and self.deadline_last_change_reason_id:
            event_data_vals.update({
                'deadline_change_reason_id':
                    self.deadline_last_change_reason_id.id,
                'deadline_change_comment': self.deadline_last_change_comment,
            })
        return super(RequestRequest, self).trigger_event(
            event_type_code, event_data_vals)

    def action_show_deadline_change_system_events(self):
        self.ensure_one()
        deadline_changed_event_type = self.env.ref(
            'generic_request.request_event_type_deadline_changed')
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_request.action_request_event_view',
            domain=[('event_type_id', '=', deadline_changed_event_type.id),
                    ('request_id', '=', self.id)],
            name=_('Deadline Change Events'))

    def action_do_change_deadline(self):
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_request_deadline.action_request_wizard_change_deadline',
            context={'default_request_id': self.id})

    @on_event('deadline-overdue', 'stage-changed', 'closed')
    def on_event_calculate_deadline_overdue(self, event):
        self._calculate_deadline_overdue()

    def _calculate_deadline_overdue(self):
        current_datetime = fields.Datetime.now()
        if self.deadline_date and self.deadline_format == 'date':
            days_diff = (self.deadline_date - current_datetime.date()).days
            deadline_overdue_days = abs(min(days_diff, 0))
            self.deadline_overdue = deadline_overdue_days * 24
        elif self.deadline_date_dt and self.deadline_format == 'datetime':
            seconds_diff = (
                (self.deadline_date_dt - current_datetime).total_seconds())
            deadline_overdue_sec = abs(min(seconds_diff, 0))
            self.deadline_overdue = deadline_overdue_sec / 3600

    def _mail_track(self, tracked_fields, initial):
        # This method override is essential for enhancing the default track
        # message, when the track field is 'deadline_date' or
        # 'deadline_date_dt'. It appends additional details regarding the
        # reason for the deadline change and the associated comment message.
        changes, tracking_value_ids = super()._mail_track(
            tracked_fields, initial)
        deadline_changed = 'deadline_date' in changes or \
                           'deadline_date_dt' in changes
        if deadline_changed and self.strict_deadline:
            reason_name = self.deadline_last_change_reason_id.name or ''
            comment = self.deadline_last_change_comment or ''
            log_note = ('<p>Deadline changed!</p> '
                        '<p>Reason: <strong>%s</strong> '
                        '<p>Comments: <i>%s</i></p>') % (reason_name, comment)
            log_note = Markup(_(
                "<p>Deadline changed!</p>"
                "<p>Reason: <strong>{reason_name}</strong></p>"
                "<p>Comments: <i>{comment}</i></p>").format(
                reason_name=reason_name,
                comment=comment))  # nosec
            self._message_log(
                body=log_note,
                tracking_value_ids=tracking_value_ids)
            return {}, []
        return changes, tracking_value_ids

    def action_calculate_deadline_overdue(self):
        self._calculate_deadline_overdue()

    @api.model
    def scheduler_update_deadline_overdue(self):
        """Update deadline_overdue for all open requests with deadlines.
        This method is called by hourly cron job.
        """
        # Find all active requests that have deadline set
        domain = [
            ('closed', '=', False),
            '|',
            ('deadline_date', '!=', False),
            ('deadline_date_dt', '!=', False),
        ]
        requests = self.search(domain)
        for request in requests:
            request._calculate_deadline_overdue()
        return True
