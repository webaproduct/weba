from odoo import models, fields, api


class YodooKnowledgeCategory(models.Model):
    _inherit = 'yodoo.knowledge.category'

    website_url = fields.Char(
        'Website URL',
        compute='_compute_website_url',
        help='The full URL to access the Knowledge '
             'Category through the website.')

    @api.depends()
    def _compute_website_url(self):
        for category in self:
            category.website_url = f'/knowledge/{category.id}'

    def action_show_on_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'self',
        }
