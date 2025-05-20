import logging

from odoo import exceptions
from odoo import models, fields, api, _
from odoo.addons.generic_mixin import pre_write, post_write, pre_create
from odoo.addons.generic_system_event import on_event

_logger = logging.getLogger(__name__)


class RequestRequest(models.Model):
    _inherit = 'request.request'

    team_id = fields.Many2one(
        'generic.team', 'Team',
        ondelete='restrict', tracking=True, index=True,
        readonly=True,
        help="Team responsible for next action on this request.")

    @on_event("team-assigned", "team-reassigned")
    def _send_default_notification_assigned_team(self, event):
        new_team_id = event.new_team_id
        assigned_user = self.user_id
        if assigned_user:
            team_member = assigned_user.get_team_member(new_team_id)
            if team_member:
                team_member.write({'last_assign_time': fields.Datetime.now()})
        classifier = self.sudo().classifier_id
        if not classifier.send_mail_on_request_team_assigned_event:
            return

        if self.team_id and not self.user_id:
            template_id = classifier.request_team_assigned_mail_template_id
            email_values = {'is_request_default_notification_mail': True}

            self._send_default_notification__send(
                template=template_id, event=event, email_values=email_values
            )

    @on_event("assigned", "reassigned")
    def _on_assigned__generic_team_member_write_assign_time(self, event):
        new_user_id = event.new_user_id
        assigned_team = self.team_id
        if not new_user_id or not assigned_team:
            return
        team_member = new_user_id.get_team_member(assigned_team)
        if team_member:
            team_member.write({'last_assign_time': fields.Datetime.now()})

    @post_write('team_id')
    def _after_team_id_changed(self, changes):
        old_team, new_team = changes['team_id']
        event_data = {'old_team_id': old_team.id, 'new_team_id': new_team.id}
        if not old_team and new_team:
            self.trigger_event('team-assigned', event_data)
        elif old_team and new_team:
            self.trigger_event('team-reassigned', event_data)
        elif old_team and not new_team:
            self.trigger_event('team-unassigned', event_data)

    def action_request_assign(self):
        self.ensure_can_assign()
        ctx = {'default_request_ids': [(6, 0, self.ids)]}
        if self.team_id:
            ctx.update({'default_team_id': self.team_id.id})
        action = self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_request_team.action_request_team_wizard_assign',
            context=ctx,
        )
        return action

    @pre_create('team_id')
    def _before_create_update_date_assigned_when_team_supplied(self, changes):
        if changes['team_id'].new_val:
            return {
                'date_assigned': fields.Datetime.now()
            }
        return {}

    @pre_write('team_id')
    def _before_team_id_changed(self, changes):
        new_team = changes['team_id'][1]  # (old_team, new_team)
        if new_team:
            return {'date_assigned': fields.Datetime.now()}
        return {'date_assigned': False}

    def action_request_assign_to_me(self):
        if self.team_id and not self.team_id._check_user_in_team(
                self.env.user):
            # If current user does not belong to request's team,
            # then we have to clean team_id first
            self.team_id = False
        return super(RequestRequest, self).action_request_assign_to_me()

    @api.constrains('user_id', 'team_id')
    def _check_assigned_user_in_team(self):
        for rec in self:
            if not (rec.user_id and rec.team_id):
                continue
            if not rec.team_id._check_user_in_team(rec.user_id):
                raise exceptions.ValidationError(_(
                    "User '%(user)s' is not a member of team '%(team)s'."
                ) % {
                    'user': rec.user_id.display_name,
                    'team': rec.team_id.display_name,
                })
