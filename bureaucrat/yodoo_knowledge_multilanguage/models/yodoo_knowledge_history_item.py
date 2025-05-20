from odoo import models, fields


ENGLISH_LANG_ID = 1


class YodooKnowledgeItemHistory(models.Model):
    _inherit = 'yodoo.knowledge.item.history'

    language_id = fields.Many2one(
        'res.lang',
        required=True,
        default=lambda self: self.item_id.language_id or ENGLISH_LANG_ID
    )

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, f"{rec.language_id.iso_code} {rec.item_id.name}"
                         f" [{rec.date_create}]")
            )
        return result
