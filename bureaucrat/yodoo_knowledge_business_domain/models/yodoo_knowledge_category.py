from odoo import models, fields, api


class YodooKnowledgeCategory(models.Model):
    _inherit = 'yodoo.knowledge.category'

    business_domain_id = fields.Many2one(
        'yodoo.business.domain', string="Business Domain",
        domain="[('id', '!=', False)]")

    @api.model
    def create(self, vals):
        category = super().create(vals)
        category._update_child_business_domains()
        return category

    def write(self, vals):
        res = super().write(vals)
        if 'business_domain_id' in vals:
            self._update_child_business_domains()
        return res

    def _update_child_business_domains(self):
        for category in self:
            if (category.parent_id and category.business_domain_id
                    != category.parent_id.business_domain_id):
                category.business_domain_id = (
                    category.parent_id.business_domain_id)
            else:
                self.child_ids.write(
                    {'business_domain_id': category.business_domain_id})
                self.item_ids.write(
                    {'business_domain_id': category.business_domain_id})
