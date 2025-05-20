from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    read_show_resource = fields.Boolean(default=False)
    create_show_resource = fields.Boolean(default=False)
