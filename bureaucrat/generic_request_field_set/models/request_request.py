from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


def field_set_value_get(record, field_res_model):
    record.ensure_one()

    # This case, when res model is not present in pool, may
    # happen, when addon that implements this model was uninstalled.
    try:
        Model = record.env[record[field_res_model]]
    except KeyError:
        return False

    res_record = Model.search([('request_id', '=', record.id)])
    if res_record.exists():
        if len(res_record) > 1:
            raise ValidationError(_(
                'Found more than one Field Set Value for this Request!'))
        return res_record
    return Model.browse()


class RequestRequest(models.Model):
    _inherit = 'request.request'

    show_fields_set_button = fields.Boolean(
        compute='_compute_show_fields_set_button', readonly=True)
    request_classifier_id = fields.Many2one(
        'request.classifier',
        compute='_compute_current_classifier',
        readonly=True, store=True, index=True)
    field_set_type_id = fields.Many2one(
        'field.set.type',
        related='request_classifier_id.field_set_type_id',
        readonly=True, store=True, index=True)
    field_set_model_id = fields.Many2one(
        'ir.model',
        related='field_set_type_id.field_set_model_id',
        readonly=True, store=True, index=True)
    field_set_model_name = fields.Char(
        related='field_set_model_id.model',
        readonly=True, store=True, index=True)

    @api.depends('service_id', 'category_id', 'type_id')
    def _compute_current_classifier(self):
        for rec in self:
            rec.request_classifier_id = rec._get_current_classifier()

    @api.depends()
    def _compute_show_fields_set_button(self):
        for rec in self:
            if rec._check_classifier_has_field_set_type:
                rec.show_fields_set_button = True
            else:
                rec.show_fields_set_button = False

    @property
    def _check_classifier_has_field_set_type(self):
        self.ensure_one()
        if self.request_classifier_id.field_set_type_id:
            return True
        return False

    @property
    def field_set_values_record(self):
        self.ensure_one()
        return field_set_value_get(self, 'field_set_model_name')

    def action_view_related_field_values(self):
        self.ensure_one()

        if not self.request_classifier_id:
            raise ValidationError(_('No Classifier found!'))

        if not self.field_set_type_id:
            raise ValidationError(_(
                'The Field Set Type setting is not specified in the Classifier'
                ' for this Request!'))

        values = {
            'type': 'ir.actions.act_window',
            'name': 'Field set values',
            'res_model': self.field_set_model_name,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
            },
        }
        res_record = field_set_value_get(self, 'field_set_model_name')
        if res_record:
            values.update({'res_id': res_record.id})

        return values
