from odoo import models, fields, api


class FieldSetType(models.Model):
    _name = 'field.set.type'
    _description = 'Requests: Field Set Type'

    name = fields.Char(required=True, index=True, translate=True)
    field_set_model_id = fields.Many2one(
        'ir.model',
        required=True, index=True, ondelete='cascade', tracking=True,
        domain=[
            ('is_generic_request_field_set', '=', True),
            ('model', '!=', 'generic.request.field.set.mixin')
        ])
    field_set_model_name = fields.Char(
        related='field_set_model_id.model', readonly=True,
        store=True, index=True)
    field_set_model_state = fields.Selection(
        related='field_set_model_id.state', readonly=True
    )
    field_set_count = fields.Integer(
        compute='_compute_field_set_count'
    )

    @api.depends()
    def _compute_field_set_count(self):
        for field_set_type in self:
            model_name = field_set_type.field_set_model_name
            field_set_type.field_set_count = self.env[
                model_name].sudo().search_count([])
