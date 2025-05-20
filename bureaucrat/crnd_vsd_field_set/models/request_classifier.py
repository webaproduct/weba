from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    read_show_field_set = fields.Boolean(
        readonly=False,
    )
    create_show_field_set = fields.Boolean(
        readonly=False,
    )
