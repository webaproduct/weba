from odoo import models


class MergePartnerAutomatic(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    def action_merge(self):
        res = super(MergePartnerAutomatic, self).action_merge()
        self.env['res.partner'].flush_model(fnames=['request_ids'])
        self.dst_partner_id.modified(fnames=[
            'request_by_partner_ids', 'request_by_author_ids'
        ])
        self.dst_partner_id.flush_model(fnames=[
            'request_by_partner_ids', 'request_by_author_ids'
        ])
        return res
