from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    field_set_type_id = fields.Many2one(
        'field.set.type', index=True, ondelete='cascade', required=False)
