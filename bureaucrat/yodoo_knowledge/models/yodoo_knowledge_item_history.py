from odoo import models, fields

DOC_TYPE = [
    ('html', 'html'),
    ('pdf', 'pdf'),
]


class YodooKnowledgeItemHistory(models.Model):
    _name = 'yodoo.knowledge.item.history'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    _description = 'Yodoo Knowledge: Item History'
    _order = 'date_create DESC'

    _auto_set_noupdate_on_write = True

    commit_summary = fields.Char()
    item_name = fields.Char()
    item_format = fields.Selection(
        selection=DOC_TYPE, required=True)
    item_body_html = fields.Html()
    item_body_pdf = fields.Binary(attachment=True)
    user_id = fields.Many2one(
        'res.users',
        index=True, required=True, readonly=True,
        default=lambda self: self.env.user.id,
    )
    date_create = fields.Datetime(
        default=fields.Datetime.now,
        index=True, required=True, readonly=True)
    item_id = fields.Many2one(
        'yodoo.knowledge.item',
        ondelete='cascade', index=True, required=True, readonly=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, "%s [%s]" % (rec.item_id.name, rec.date_create))
            )
        return result
