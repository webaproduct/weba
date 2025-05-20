from odoo import models, fields, api, exceptions, _


class IrModel(models.Model):
    _inherit = 'ir.model'

    is_generic_request_field_table = fields.Boolean(
        default=False,
        help="Whether this model is Generic Field Table.",
    )

    def write(self, vals):
        if self and 'is_generic_request_field_table' in vals:
            # Guard agains modification of base models
            if not all(rec.state == 'manual' for rec in self):
                raise exceptions.UserError(_(
                    'Only custom models can be modified.'))

            # Do not allow undo making model generic request field table
            if (not vals['is_generic_request_field_table'] and
                    any(rec.is_generic_request_field_table for rec in self)):
                raise exceptions.UserError(_(
                    "Field 'Is Generic Field Table' cannot be changed "
                    "to 'False'."))

            res = super(IrModel, self).write(vals)
            self.env.flush_all()
            # tableup models; this reloads custom models in registry
            self.pool.tableup_models(self._cr)
            # update database schema of models
            self.pool.init_models(
                self._cr,
                self.pool.descendants(self.mapped('model'), '_inherits'),
                dict(self._context, update_custom_fields=True))
        else:
            res = super(IrModel, self).write(vals)
        return res

    def _reflect_model_params(self, model):
        vals = super(IrModel, self)._reflect_model_params(model)
        vals['is_generic_request_field_table'] = issubclass(
            type(model), self.pool['generic.request.field.table.mixin'])
        return vals

    @api.model
    def _instanciate(self, model_data):
        model_class = super(IrModel, self)._instanciate(model_data)
        if (model_data.get('is_generic_request_field_table') and
                model_class._name != 'generic.request.field.table.mixin'):
            parents = model_class._inherit or []
            if isinstance(parents, str):
                parents = [parents]
            model_class._inherit = (
                parents + ['generic.request.field.table.mixin'])
        return model_class
