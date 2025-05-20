from odoo import models, fields, api


class FieldTableType(models.Model):
    _name = 'field.table.type'
    _description = 'Requests: Field Table Type'

    name = fields.Char(required=True, index=True, translate=True)
    field_table_model_id = fields.Many2one(
        'ir.model',
        required=True, index=True, ondelete='cascade', tracking=True,
        domain=[
            ('is_generic_request_field_table', '=', True),
            ('model', '!=', 'generic.request.field.table.mixin')
        ])
    field_table_model_name = fields.Char(
        related='field_table_model_id.model', readonly=True,
        store=True, index=True)
    field_table_model_state = fields.Selection(
        related='field_table_model_id.state', readonly=True
    )
    field_table_count = fields.Integer(
        compute='_compute_field_table_count'
    )

    @api.depends()
    def _compute_field_table_count(self):
        for field_table_type in self:
            model_name = field_table_type.field_table_model_name
            field_table_type.field_table_count = self.env[
                model_name].sudo().search_count([])
