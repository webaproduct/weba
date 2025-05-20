from odoo import models, fields, api


class CRMLead(models.Model):
    _inherit = "crm.lead"

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, summary='', note='', **act_values):
        res = super().activity_schedule(act_type_xmlid, date_deadline, summary, note, **act_values)
        for lead in self:
            for user in lead.message_follower_ids.mapped('partner_id.user_ids') - self.env.user:
                user.sudo().notify_info(message=f'New message/activity for lead {lead.name} was posted')
        return res
