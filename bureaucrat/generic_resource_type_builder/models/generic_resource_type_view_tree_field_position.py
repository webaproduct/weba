from odoo import models, fields
from odoo.addons.generic_mixin import post_write, post_create


class GenericResourceTypeViewTreeFieldPosition(models.Model):
    _name = 'generic.resource.type.view.tree.field.position'
    _inherit = [
        'generic.mixin.track.changes',
    ]

    resource_type_id = fields.Many2one(
        comodel_name='generic.resource.type',
        readonly=True)
    custom_field_id = fields.Many2one(
        comodel_name='generic.resource.type.custom.field',
        ondelete='cascade',
        required=True,
    )
    custom_field_name = fields.Char(
        related='custom_field_id.field_description',
        readonly=True)
    custom_field_ttype = fields.Selection(
        related='custom_field_id.ttype',
        readonly=True)
    sequence = fields.Integer(
        default=5, index=True)

    _sql_constraints = [
        ('custom_field_id_uniq',
         'UNIQUE (custom_field_id)',
         'Field in Tree View must be unique!'),
    ]

    @post_create()
    @post_write('sequence')
    def _post_write_generate_tree_view(self, changes):
        """
        Regenerate the tree view based on the 'sequence'
        field changes.

        This method is executed after the creation of a new record
        or when the field 'sequence' was updated.
        It triggers the complete regeneration of the tree view.

        :return: None
        """
        self.resource_type_id._regenerate_tree_view()

    def unlink(self):
        # It is needed to regenerate tree view,
        # when tree position record deleted
        resource_type_id = self.resource_type_id
        res = super(GenericResourceTypeViewTreeFieldPosition, self).unlink()
        resource_type_id._regenerate_tree_view()
        return res
