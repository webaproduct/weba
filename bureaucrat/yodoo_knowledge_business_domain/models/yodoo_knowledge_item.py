from odoo import models, fields, api


class YodooKnowledgeItem(models.Model):
    _inherit = 'yodoo.knowledge.item'

    business_domain_id = fields.Many2one(
        'yodoo.business.domain', string="Business Domain",
        domain="[('id', '!=', False)]")

    @api.depends('category_id', 'category_id.business_domain_id')
    def _compute_business_domain(self):
        for record in self:
            record.business_domain_id = record.category_id.business_domain_id
