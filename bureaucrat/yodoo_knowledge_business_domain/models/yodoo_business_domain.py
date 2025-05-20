from odoo import models, fields


class YodooBusinessDomain(models.Model):
    _inherit = "yodoo.business.domain"

    knowledge_item_ids = fields.One2many(
        'yodoo.knowledge.item', 'business_domain_id', auto_join=True)
