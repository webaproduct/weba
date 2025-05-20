from urllib.parse import urlencode, quote_plus

from odoo import api, fields, models


class YodooKnowledgeItemHistory(models.Model):
    _inherit = 'yodoo.knowledge.item.history'

    pdf_src_url = fields.Char(compute='_compute_src_url', store=False)

    @api.depends('item_format')
    def _compute_src_url(self):
        for record in self:
            if record.item_format == 'pdf':
                query_obj = {
                    'model': 'yodoo.knowledge.item.history',
                    'field': 'item_body_pdf',
                    'id': record.id,
                }
                fileURI = (f"/web/image?"
                           f"{urlencode(query_obj, quote_via=quote_plus)}")
                viewerURL = '/web/static/lib/pdfjs/web/viewer.html?'
                record.pdf_src_url = viewerURL + urlencode({'file': fileURI})
            else:
                record.pdf_src_url = False
