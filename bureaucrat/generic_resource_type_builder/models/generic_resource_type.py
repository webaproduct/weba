from odoo import models, fields

from lxml import etree  # nosec

TREE_VIEW_DEFAULT_ARCH = """<?xml version="1.0"?>
    <tree create='true'>
        <field name="x_name"/>
        <field name="resource_id" string="Resource"/>
        <field name="resource_visibility"/>
    </tree>"""

FORM_VIEW_DEFAULT_ARCH = """<?xml version="1.0"?>
    <data>
        <xpath expr="/form" position="attributes">
            <attribute name="create">true</attribute>
            <attribute name="delete">true</attribute>
        </xpath>
        <xpath expr="//page[1]" position="before">
            <page name="page_info" string="Info">
                <group name="group_info_root">
                    <group name="group_info_left">
                        <field name="x_name"/>
                        <field name="resource_id"
                            string="Resource" placeholder="Resource"
                            required="False"
                            readonly="True"/>
                    </group>
                    <group name="group_info_right">
                    </group>
                </group>
            </page>
        </xpath>
    </data>
"""

# The mapping of selection field 'place_on_form' of the field
# and the group on form view which the field belongs to
GROUPS_MAPPING = {
    'left_slot': 'group_info_left',
    'right_slot': 'group_info_right'
}


class GenericResourceType(models.Model):
    _inherit = 'generic.resource.type'

    custom_field_ids = fields.One2many(
        comodel_name='generic.resource.type.custom.field',
        inverse_name='resource_type_id',
        readonly=False)
    field_tree_position_ids = fields.One2many(
        comodel_name='generic.resource.type.view.tree.field.position',
        inverse_name="resource_type_id")
    field_form_position_ids = fields.One2many(
        comodel_name='generic.resource.type.view.form.field.position',
        inverse_name="resource_type_id")
    model_tree_view_id = fields.Many2one(
        comodel_name='ir.ui.view',
        readonly=True)
    model_form_view_id = fields.Many2one(
        comodel_name='ir.ui.view',
        readonly=True)

    def _get_default_arch(self):
        root = etree.XML(FORM_VIEW_DEFAULT_ARCH)
        if self.model_id.is_mail_thread:
            # Build parent elements for chatter and append to view
            chatter_root_xpath = etree.Element(
                _tag='xpath',
                attrib={
                    "expr": "/form/sheet",
                    "position": "after"})
            chatter_root_el = etree.Element(
                _tag='div',
                attrib={"class": "oe_chatter"})
            chatter_root_xpath.append(chatter_root_el)

            # Build chatter element
            # and append to parent
            chatter_mail_el = etree.Element(
                _tag='field',
                attrib={
                    "name": "message_ids",
                    "widget": "mail_thread"})
            chatter_root_el.append(chatter_mail_el)

            # Build activity element and append
            # to parent if needed
            if self.model_id.is_mail_activity:
                chatter_activity_el = etree.Element(
                    _tag='field',
                    attrib={
                        "name": "message_follower_ids",
                        "widget": "mail_followers"})
                chatter_root_el.append(chatter_activity_el)

            # Append chatter elements to root
            root.append(chatter_root_xpath)
        return etree.tostring(root, encoding='utf-8')

    def _prepare_model_view_values(self, view_name, view_type, model):
        view_values = {
            'name': view_name,
            'model': model.model,
            'mode': 'primary',
            'type': view_type,
            'xml_id': '__generic_resource_type_builder.%s__' % model.model,
        }
        if view_type == 'tree':
            view_values.update({'arch': TREE_VIEW_DEFAULT_ARCH})
        elif view_type == 'form':
            view_values.update({
                'arch': self._get_default_arch(),
                'inherit_id': self.env.ref(
                    'generic_resource.generic_resource_view_form_base').id,
            })
        else:
            view_values.update({'arch': '<data></data>'})
        return view_values

    def _create_model_views(self, model):
        View = self.env['ir.ui.view']

        # Tree View
        tree_view_values = self._prepare_model_view_values(
            view_name='%s Tree View' % model.name,
            view_type='tree',
            model=model)
        tree_view = View.sudo().create(tree_view_values)
        # Create model data to generate xml_id
        self.env['ir.model.data'].create({
            'module': '__generic_resource_type_builder__',
            'name': '%s_tree_view' % model.model,
            'model': tree_view._name,
            'res_id': tree_view.id,
        })

        # Form View
        form_view_values = self._prepare_model_view_values(
            view_name='%s Form View' % model.name,
            view_type='form',
            model=model)
        form_view = View.sudo().create(form_view_values)
        # Create model data to generate xml_id
        self.env['ir.model.data'].create({
            'module': '__generic_resource_type_builder__',
            'name': '%s_form_view' % model.model,
            'model': form_view._name,
            'res_id': form_view.id,
        })
        self.model_form_view_id = form_view
        self.model_tree_view_id = tree_view

    def _regenerate_tree_view(self):
        """
        Regenerate the tree view by recreating it from scratch.

        This method regenerates the tree view completely by removing all
        existing field elements from the XML tree of the view and adding
        them back in the desired order based on the custom field sequence.
        It then updates the tree view with the modified XML.

        :return: None
        """
        default_arch = TREE_VIEW_DEFAULT_ARCH
        model_tree_view = self.model_tree_view_id
        doc = etree.XML(default_arch)
        sorted_fields = self.field_tree_position_ids.sorted(
            key=lambda field: field.sequence)
        for field in sorted_fields:
            el = etree.Element('field', name=field.custom_field_id.name)
            doc.append(el)
        model_tree_view.write({'arch': etree.tostring(doc, encoding='utf-8')})

    def _regenerate_form_view(self):
        """
        Regenerate the form view by recreating it from scratch.

        This method regenerates the form view completely by removing all
        existing field elements from the XML tree of the view and adding
        them back in the desired order based on the custom field sequence.
        It then updates the form view with the modified XML.

        :return: None
        """
        default_arch = self._get_default_arch()
        model_form_view = self.model_form_view_id
        doc = etree.XML(default_arch)
        sorted_fields = self.field_form_position_ids.sorted(
            key=lambda field: field.sequence)
        for field in sorted_fields:
            root = doc.find(".//group[@name='%s']" % GROUPS_MAPPING.get(
                field.place_on_form))
            el = etree.Element('field', name=field.custom_field_id.name)
            root.append(el)
        model_form_view.write({'arch': etree.tostring(doc, encoding='utf-8')})
