from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slugify


class YodooBusinessDomain(models.Model):
    # pylint: disable=too-many-locals
    _name = "yodoo.business.domain"
    _description = "Yodoo Business Domain"
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char()

    active = fields.Boolean(default=True, index=True)

    description = fields.Text(translate=True)
    help_html = fields.Html(translate=True)

    @api.model
    def create(self, vals):
        if not vals.get('code') and vals.get('name'):
            vals['code'] = slugify(vals['name'])
        return super().create(vals)

    def write(self, vals):
        if 'name' in vals and not vals.get('code'):
            vals['code'] = slugify(vals['name'])
        return super().write(vals)
