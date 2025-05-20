from odoo import models, fields
from odoo.addons.generic_mixin import post_write, post_create


class GenericResourceTypeViewFormFieldPosition(models.Model):
    _name = 'generic.resource.type.view.form.field.position'
    _inherit = [
        'generic.mixin.track.changes',
    ]

    resource_type_id = fields.Many2one(
        comodel_name='generic.resource.type',
        required=True,
        index=True,
        readonly=True,
        ondelete='cascade'
    )
    custom_field_id = fields.Many2one(
        comodel_name='generic.resource.type.custom.field',
        required=True,
        ondelete='cascade'
    )
    custom_field_name = fields.Char(
        related='custom_field_id.field_description',
        readonly=True)
    custom_field_ttype = fields.Selection(
        related='custom_field_id.ttype',
        readonly=True)
    place_on_form = fields.Selection([
        ('left_slot', 'Left slot'),
        ('right_slot', 'Right slot'),
    ], default='left_slot', required=True)
    sequence = fields.Integer(
        default=5, index=True)

    _sql_constraints = [
        ('custom_field_id_uniq',
         'UNIQUE (custom_field_id)',
         'Field in Form View must be unique!'),
    ]

    @post_create()
    @post_write('sequence', 'place_on_form')
    def _post_write_generate_form_view(self, changes):
        """
        Regenerate the form view based on the 'place_on_form' or 'sequence'
        field changes.

        This method is executed after the creation of a new record
        or when the fields 'place_on_form' or 'sequence' was updated.
        It triggers the complete regeneration of the form view.

        :return: None
        """
        self.resource_type_id._regenerate_form_view()

    def unlink(self):
        # It is needed to regenerate form view,
        # when form position record deleted
        resource_type_id = self.resource_type_id
        res = super(GenericResourceTypeViewFormFieldPosition, self).unlink()
        resource_type_id._regenerate_form_view()
        return res
