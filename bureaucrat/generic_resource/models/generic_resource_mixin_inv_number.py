import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class GenericResourceMixinInvNumber(models.AbstractModel):
    ''' generic_resource_mixin_inv_number model is meant to be inherited by
     any model that needs to have automatically generated field inv_number for
     inventory number.
     To use it, you must create sequence in "ir.sequence" model in data
     directory.
     For example:
        <record id="id_for_your_sequence" model="ir.sequence">
            <field name="name">name_for_your_sequence</field>
            <field name="code">code_for_your_sequence</field>
            <field name="prefix">prefix_for_your_inv_number</field>
            <field name="padding">count_of_integer_in_your_inv_number</field>
        </record>

     And use it in model definition. For example:

     class YourModel(models.Model):
         _name = 'your.model'
         _inherit = 'generic.resource.mixin.inv.number'

         _inv_number_seq_code = 'your_addon.id_for_your_sequence'

     It's all!
     Field inv_number will be automatically added to your model.
     Values for it will be generated by sequence
      'your_addon.id_for_your_sequence'.
     '''
    _name = 'generic.resource.mixin.inv.number'
    _inherit = [
        'generic.mixin.namesearch.by.fields',
    ]
    _description = 'Generic Resource Mixin Inv Number'

    _generic_namesearch_fields = ['inv_number']
    _generic_namesearch_search_by_rec_name = True

    _inv_number_seq_code = None
    _inv_number_in_display_name = False

    inv_number = fields.Char(
        'Inventory Number', index=True, required=True,
        readonly=True, default='', copy=False)

    @api.model_create_multi
    def create(self, vals):
        values = []
        for val in vals:
            # Copy value, that could be modified
            value = dict(val)
            # Set inv_number if needed
            if self._inv_number_seq_code is not None and (
                    not value.get('inv_number')):
                value['inv_number'] = self.env['ir.sequence'].next_by_code(
                    self._inv_number_seq_code)
            values += [value]
        result = super(GenericResourceMixinInvNumber, self).create(values)
        return result

    @api.depends('inv_number')
    def _compute_display_name(self):
        if not self._inv_number_in_display_name:
            return super()._compute_display_name()

        result = []
        for rec in self:
            rec.display_name = \
                ("%s [%s]" % (rec.name, rec.inv_number))
            result.append(rec.display_name)
        return result
