from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    read_show_tags = fields.Boolean(default=False)
    create_show_tags = fields.Boolean(default=False)
