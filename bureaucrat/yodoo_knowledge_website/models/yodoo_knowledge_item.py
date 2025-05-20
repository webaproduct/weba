from urllib.parse import urlencode, quote_plus

from odoo import api, fields, models


class YodooKnowledgeItem(models.Model):
    _inherit = 'yodoo.knowledge.item'

    pdf_src_url = fields.Char(compute='_compute_src_url', store=False)

    website_url = fields.Char(
        'Website URL',
        compute='_compute_website_url',
        help='The full URL to access the document through the website.')

    @api.depends('item_format')
    def _compute_src_url(self):
        for record in self:
            if record.item_format == 'pdf':
                query_obj = {
                    'model': 'yodoo.knowledge.item',
                    'field': 'item_body_pdf',
                    'id': record.id,
                }
                fileURI = (f"/web/image?"
                           f"{urlencode(query_obj, quote_via=quote_plus)}")
                viewerURL = '/web/static/lib/pdfjs/web/viewer.html?'
                record.pdf_src_url = viewerURL + urlencode({'file': fileURI})
            else:
                record.pdf_src_url = False

    @api.depends()
    def _compute_website_url(self):
        for item in self:
            item.website_url = f"/knowledge/item/{item.id}"

    def action_show_on_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'self',
        }
