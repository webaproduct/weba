from odoo import models, fields, api


class GenericResourceTypeCustomField(models.Model):
    _name = 'generic.resource.type.custom.field'
    _inherit = [
        'generic.mixin.track.changes',
    ]

    resource_type_id = fields.Many2one(
        comodel_name='generic.resource.type',
        required=True,
        index=True,
        ondelete='cascade')
    ir_model_custom_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        ondelete='cascade',
        delegate=True)
    tree_position_ids = fields.One2many(
        comodel_name='generic.resource.type.view.tree.field.position',
        inverse_name='custom_field_id',
        readonly=True,
        help='Technical field to keep reference to related '
             'tree_position_id',
    )
    tree_position_id = fields.Many2one(
        comodel_name='generic.resource.type.view.tree.field.position',
        readonly=True,
        store=True,
        compute='_compute_tree_position_id',
    )
    show_on_tree = fields.Boolean(
        compute='_compute_show_on_tree',
        inverse='_inverse_show_on_tree',
        store=True,
        help="If set to True, then system will generate "
             "tree position record for this field",
    )
    form_position_ids = fields.One2many(
        comodel_name='generic.resource.type.view.form.field.position',
        inverse_name='custom_field_id'
    )
    form_position_id = fields.Many2one(
        comodel_name='generic.resource.type.view.form.field.position',
        readonly=True,
        store=True,
        compute='_compute_form_position_id',
    )
    show_on_form = fields.Boolean(
        compute='_compute_show_on_form',
        inverse='_inverse_show_on_form',
        store=True,
        help="If set to True, then system will generate "
             "default form position record for this field",
    )

    # // Tree positioning part //
    @api.depends("tree_position_id")
    def _compute_show_on_tree(self):
        for record in self:
            if len(record.tree_position_id) == 1:
                record.show_on_tree = True
            else:
                record.show_on_tree = False

    @api.depends("tree_position_ids")
    def _compute_tree_position_id(self):
        for record in self:
            if len(record.tree_position_ids) == 1:
                record.tree_position_id = (
                    record.tree_position_ids[0])
            else:
                record.tree_position_id = False

    def _inverse_show_on_tree(self):
        Tree_position = self.env[
            'generic.resource.type.view.tree.field.position']
        for record in self:
            if record.show_on_tree and not record.tree_position_id:
                tree_position_data = record._prepare_tree_position_data()
                record.tree_position_id = Tree_position.create(
                    tree_position_data)
            elif not record.show_on_tree and record.tree_position_id:
                record.tree_position_id.unlink()

    def _prepare_tree_position_data(self):
        self.ensure_one()
        return {
            'resource_type_id': self.resource_type_id.id,
            'custom_field_id': self.id,
        }

    # // Form positioning part //
    @api.depends("form_position_id")
    def _compute_show_on_form(self):
        for record in self:
            if len(record.form_position_id) == 1:
                record.show_on_form = True
            else:
                record.show_on_form = False

    @api.depends("form_position_ids")
    def _compute_form_position_id(self):
        for record in self:
            if len(record.form_position_ids) == 1:
                record.form_position_id = (
                    record.form_position_ids[0])
            else:
                record.form_position_id = False

    def _inverse_show_on_form(self):
        Form_position = self.env[
            'generic.resource.type.view.form.field.position']
        for record in self:
            if record.show_on_form and not record.form_position_id:
                form_position_data = record._prepare_form_position_data()
                record.form_position_id = Form_position.create(
                    form_position_data)
            elif not record.show_on_form and record.form_position_id:
                record.form_position_id.unlink()

    def _prepare_form_position_data(self):
        self.ensure_one()
        return {
            'resource_type_id': self.resource_type_id.id,
            'custom_field_id': self.id,
        }

    @api.model
    def create(self, vals):
        resource_type_id = vals.get('resource_type_id', False)
        if resource_type_id:
            resource_type = self.env['generic.resource.type'].browse(
                resource_type_id)
            vals = dict(vals, model_id=resource_type.model_id.id)
        res = super(GenericResourceTypeCustomField, self).create(vals)
        return res

    def unlink(self):
        # This is needed to properly handle delete custom field
        # Deletion must occur in the following order:
        # - delete custom field
        # - delete tree and form positions of that field (processed oncascade)
        # - regenerate views to remove custom field there
        # - delete ir.model.field
        resource_type_id = self.resource_type_id
        ir_model_field_id = self.ir_model_custom_field_id
        res = super(GenericResourceTypeCustomField, self).unlink()
        resource_type_id._regenerate_form_view()
        resource_type_id._regenerate_tree_view()
        ir_model_field_id.unlink()
        return res
