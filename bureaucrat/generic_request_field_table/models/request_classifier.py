from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    field_table_type_id = fields.Many2one(
        'field.table.type', index=True, ondelete='cascade', required=False)
