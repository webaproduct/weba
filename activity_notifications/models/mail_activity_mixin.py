from markupsafe import Markup

from odoo import models


class MailActivityMixin(models.AbstractModel):
    _inherit = "mail.activity.mixin"

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, summary='', note='', **act_values):
        res = super().activity_schedule(act_type_xmlid, date_deadline, summary, note, **act_values)
        for obj in self:
            if hasattr(obj, 'message_follower_ids'):
                for user in obj.message_follower_ids.mapped('partner_id.user_ids') - self.env.user:
                    user.sudo().notify_info(message=f'New activity for {obj._get_record_card_link()} was posted')
        return res

    def _get_record_card_link(self, title=None):
        self.ensure_one()
        url = '/web#id=%s&view_type=form&model=%s' % (self.id, self._name)
        return Markup("<a href=%s data-oe-model='%s' data-oe-id='%s'>%s</a>") % (url, self._name, self.id, title or self.display_name)