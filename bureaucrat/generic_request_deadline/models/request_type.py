from odoo import models, fields


class RequestType(models.Model):
    _inherit = 'request.type'

    use_strict_deadline = fields.Boolean(
        default=False,
        help='Use wizard to change deadline with reasons of changing')
