from odoo.tests.common import TransactionCase, Form, tagged
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.generic_mixin.tests.common import (
    ReduceLoggingMixin,
)

from lxml import etree  # nosec


def get_fields_order_in_parent_from_arch(arch, parent=None):
    """
    Retrieves the order of fields in the specified
    parent element from an XML architecture.

    Args:
        arch (str): The XML architecture as a string.
        parent (str, optional): The parent element's tag name.
                                If provided, the order of fields within
                                this parent element will be returned.
                                If not provided, the order of fields in
                                the root element will be returned.

    Returns:
        dict or False: A dictionary containing the field names as keys
                       and their corresponding order as values.
                       The order is represented by an integer. If the specified
                       parent element is not found in the XML architecture,
                       or if the architecture is invalid, False is returned.

    Examples:
        XML architecture:
        <root>
            <field name="A" />
            <field name="B" />
            <field name="C" />
        </root>

        get_fields_order_in_parent_from_arch(arch)
            # Returns: {'A': 0, 'B': 1, 'C': 2}
        get_fields_order_in_parent_from_arch(arch, 'root')
            # Returns: {'A': 0, 'B': 1, 'C': 2}
        get_fields_order_in_parent_from_arch(arch, 'parent')
        # Returns: False
        """
    root = etree.XML(arch)
    if root is None:
        return False
    if parent:
        parent_tag = root.find(parent)
        if parent_tag is not None:
            return {i.attrib['name']: v
                    for v, i in enumerate(parent_tag.iter('field'))}
        return False
    return {i.attrib['name']: v
            for v, i in enumerate(root.iter('field'))}


def sanitize_name_for_xml_id(value):
    # this method repeat behaviour when creates name for xml_id
    # in module 'generic.resource.type.wizard.create'
    # used here to simplify tests
    sanitized_value = value.replace('.', '_').replace(' ', '_').lower()
    return sanitized_value


@tagged("-at_install", "post_install")
class TestResourceTypeBuilder(ReduceLoggingMixin, TransactionCase):
    # pylint: disable=pointless-string-statement
    # pylint: disable=too-many-statements

    @classmethod
    def setUpClass(cls):
        super(TestResourceTypeBuilder, cls).setUpClass()
        # Groups
        cls.group_resource_manager = cls.env.ref(
            'generic_resource.group_generic_resource_manager')
        cls.group_resource_user = cls.env.ref(
            'generic_resource.group_generic_resource_user')
        cls.group_resource_user_implicit = cls.env.ref(
            'generic_resource.group_generic_resource_user_implicit')
        cls.group_system = cls.env.ref(
            'base.group_system')
        cls.group_portal = cls.env.ref(
            'base.group_portal')
        cls.group_public = cls.env.ref(
            'base.group_public')

    def test_wizard_create_resource_model(self):
        WIZARD = self.env['generic.resource.type.wizard.create']
        # Create resource model via wizard
        with Form(WIZARD) as model_wizard:
            model_wizard.name = 'Test Resource Model'
            model_wizard.model = 'x_test_resource_model'
            model_wizard.enable_chatter = True
            model_wizard.enable_mail_activity = True
            model_wizard.save().action_do_create_resource_type()
        resource_model = self.env['ir.model'].search([
            ('model', '=', 'x_test_resource_model')])
        self.assertTrue(resource_model.is_mail_activity)
        self.assertTrue(resource_model.is_mail_thread)
        self.assertTrue(resource_model.is_generic_resource)
        self.assertTrue(resource_model.resource_type_id)
        self.assertTrue(resource_model.generic_resource_code)
        self.assertEqual(resource_model.generic_resource_code,
                         slugify(resource_model.name))
        self.assertTrue(resource_model.resource_type_id.code)
        self.assertEqual(resource_model.resource_type_id.code,
                         resource_model.generic_resource_code)
        self.assertEqual(
            resource_model.resource_type_id.name, resource_model.name)

        # Check resource model ir.model.data created properly
        model_model_data = self.env['ir.model.data'].search([
            ('res_id', '=', resource_model.id),
            ('model', '=', 'ir.model')])
        self.assertTrue(model_model_data)
        self.assertEqual(
            model_model_data.module,
            '__generic_resource_type_builder__')
        self.assertEqual(
            model_model_data.name,
            'model_%s' % resource_model.model)
        self.assertEqual(
            model_model_data.complete_name,
            '__generic_resource_type_builder__.model_%s'
            % resource_model.model)
        # Check xml_id
        self.assertTrue(self.env.ref(model_model_data.complete_name).exists())

        # Ensure access records created
        self.assertTrue(resource_model.access_ids)
        self.assertEqual(len(resource_model.access_ids), 4)
        self.assertIn(
            self.group_resource_user_implicit,
            resource_model.access_ids.group_id)
        self.assertIn(
            self.group_resource_user,
            resource_model.access_ids.group_id)
        self.assertIn(
            self.group_portal,
            resource_model.access_ids.group_id)
        self.assertIn(
            self.group_public,
            resource_model.access_ids.group_id)

        # Check resource model acl ir.model.data created properly
        user_acl = resource_model.access_ids.filtered(
            lambda x: x.group_id == self.group_resource_user)
        user_implicit_acl = resource_model.access_ids.filtered(
            lambda x: x.group_id == self.group_resource_user_implicit)

        user_acl_model_data = self.env['ir.model.data'].search([
            ('module', '=', '__generic_resource_type_builder__'),
            ('model', '=', 'ir.model.access'),
            ('res_id', '=', user_acl.id)])
        self.assertTrue(user_acl_model_data)
        self.assertEqual(
            user_acl_model_data.module,
            '__generic_resource_type_builder__')
        self.assertEqual(
            user_acl_model_data.name,
            'access_%s_%s' % (
                resource_model.model,
                sanitize_name_for_xml_id(user_acl.name)))
        self.assertEqual(
            user_acl_model_data.complete_name,
            '__generic_resource_type_builder__.access_%s_%s' % (
                resource_model.model,
                sanitize_name_for_xml_id(user_acl.name)))
        # Check xml_id
        self.assertTrue(
            self.env.ref(user_acl_model_data.complete_name).exists())

        user_implicit_acl_model_data = self.env['ir.model.data'].search([
            ('module', '=', '__generic_resource_type_builder__'),
            ('model', '=', 'ir.model.access'),
            ('res_id', '=', user_implicit_acl.id)])
        self.assertTrue(user_implicit_acl_model_data)
        self.assertEqual(
            user_implicit_acl_model_data.module,
            '__generic_resource_type_builder__')
        self.assertEqual(
            user_implicit_acl_model_data.name,
            'access_%s_%s' % (
                resource_model.model,
                sanitize_name_for_xml_id(user_implicit_acl.name)))
        self.assertEqual(
            user_implicit_acl_model_data.complete_name,
            '__generic_resource_type_builder__.access_%s_%s' % (
                resource_model.model,
                sanitize_name_for_xml_id(user_implicit_acl.name)))
        # Check xml_id
        self.assertTrue(
            self.env.ref(user_implicit_acl_model_data.complete_name).exists())

        # Ensure resource type created for that model
        self.assertTrue(resource_model.resource_type_id.exists())

        # Ensure views are created
        self.assertTrue(resource_model.view_ids)
        form_view = resource_model.view_ids.filtered(
            lambda x: x.type == 'form')
        self.assertTrue(form_view.exists())
        tree_view = resource_model.view_ids.filtered(
            lambda x: x.type == 'tree')
        self.assertTrue(tree_view.exists())

        # Check resource model views ir.model.data
        form_view_model_data = self.env['ir.model.data'].search([
            ('module', '=', '__generic_resource_type_builder__'),
            ('model', '=', 'ir.ui.view'),
            ('res_id', '=', form_view.id)])
        self.assertTrue(form_view_model_data)
        self.assertEqual(
            form_view_model_data.module,
            '__generic_resource_type_builder__')
        self.assertEqual(
            form_view_model_data.name,
            '%s_form_view' % resource_model.model)
        self.assertEqual(
            form_view_model_data.complete_name,
            '__generic_resource_type_builder__.%s_form_view'
            % resource_model.model)
        # Check xml_id
        self.assertTrue(
            self.env.ref(form_view_model_data.complete_name).exists())

        tree_view_model_data = self.env['ir.model.data'].search([
            ('module', '=', '__generic_resource_type_builder__'),
            ('model', '=', 'ir.ui.view'),
            ('res_id', '=', tree_view.id)])
        self.assertTrue(tree_view_model_data)
        self.assertEqual(
            tree_view_model_data.module,
            '__generic_resource_type_builder__')
        self.assertEqual(
            tree_view_model_data.name,
            '%s_tree_view' % resource_model.model)
        self.assertEqual(
            tree_view_model_data.complete_name,
            '__generic_resource_type_builder__.%s_tree_view'
            % resource_model.model)
        # Check xml_id
        self.assertTrue(
            self.env.ref(tree_view_model_data.complete_name).exists())

    def test_create_custom_fields(self):
        # Create resource model via wizard
        wizard = self.env['generic.resource.type.wizard.create'].create({
            'name': 'Test Resource Model',
            'model': 'x_test_resource_model',
            'enable_chatter': True,
            'enable_mail_activity': True,
        })
        wizard.action_do_create_resource_type()
        resource_model = self.env['ir.model'].search([
            ('model', '=', wizard.model)])

        # Create custom fields
        # Ensure they align to resource model and have properly
        # created attributes
        field_char = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_char',
            'field_description': 'Field Char',
            'ttype': 'char',
            'resource_type_id': resource_model.resource_type_id.id
        })
        self.assertEqual(field_char.ir_model_custom_field_id.name,
                         field_char.name)
        self.assertIn(
            field_char.ir_model_custom_field_id, resource_model.field_id)
        self.assertEqual(field_char.ir_model_custom_field_id.ttype, 'char')
        self.assertFalse(field_char.show_on_tree)

        field_int = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_int',
            'field_description': 'Field Integer',
            'ttype': 'integer',
            'resource_type_id': resource_model.resource_type_id.id
        })
        self.assertEqual(field_int.ir_model_custom_field_id.name,
                         field_int.name)
        self.assertIn(
            field_int.ir_model_custom_field_id, resource_model.field_id)
        self.assertEqual(field_int.ir_model_custom_field_id.ttype, 'integer')
        self.assertFalse(field_int.show_on_tree)

        field_bool = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_bool',
            'field_description': 'Field Boolean',
            'ttype': 'boolean',
            'resource_type_id': resource_model.resource_type_id.id
        })
        self.assertEqual(field_bool.ir_model_custom_field_id.name,
                         field_bool.name)
        self.assertIn(
            field_bool.ir_model_custom_field_id, resource_model.field_id)
        self.assertEqual(field_bool.ttype, 'boolean')
        self.assertFalse(field_bool.show_on_tree)

        field_date = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_date',
            'field_description': 'Field Date',
            'ttype': 'date',
            'resource_type_id': resource_model.resource_type_id.id
        })
        self.assertEqual(field_date.ir_model_custom_field_id.name,
                         field_date.name)
        self.assertIn(
            field_date.ir_model_custom_field_id, resource_model.field_id)
        self.assertEqual(field_date.ttype, 'date')
        self.assertFalse(field_date.show_on_tree)

        # Try to create field alongside with adding it to tree and form view
        field_float = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_float',
            'field_description': 'Field Float',
            'ttype': 'float',
            'resource_type_id': resource_model.resource_type_id.id,
            'show_on_tree': True,
            'show_on_form': True,
        })
        self.assertEqual(field_float.ir_model_custom_field_id.name,
                         field_float.name)
        self.assertIn(
            field_float.ir_model_custom_field_id, resource_model.field_id)
        self.assertEqual(field_float.ttype, 'float')

        # Check field added to the tree view
        tree_view = field_float.resource_type_id.model_tree_view_id
        self.assertTrue(field_float.show_on_tree)
        self.assertTrue(field_float.tree_position_id)
        fields_tree_order_dict = get_fields_order_in_parent_from_arch(
            arch=tree_view.arch)
        self.assertTrue(fields_tree_order_dict.get(field_float.name))

        # Try to remove field from tree view through custom field settings
        field_float.write({
            'show_on_tree': False,
        })
        self.assertFalse(field_float.show_on_tree)
        self.assertFalse(field_float.tree_position_id)
        fields_tree_order_dict = get_fields_order_in_parent_from_arch(
            arch=tree_view.arch)
        self.assertFalse(fields_tree_order_dict.get(field_float.name))

        # Check field added to the form view
        form_view = field_float.resource_type_id.model_form_view_id
        self.assertTrue(field_float.show_on_form)
        self.assertTrue(field_float.form_position_id)
        # Check right group empty
        fields_order_right = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_right"]')
        self.assertFalse(fields_order_right)
        # Check group left
        fields_order_left = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_left"]')

        # Check field_float was added to left group by default to form
        self.assertTrue(fields_order_left.get(field_float.name))

        # Try to remove field from form view through custom field settings
        field_float.write({
            'show_on_form': False,
        })
        self.assertFalse(field_float.show_on_form)
        self.assertFalse(field_float.form_position_id)
        fields_order_left = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_left"]')
        self.assertFalse(fields_order_left.get(field_float.name))

    def test_tree_fields_positions(self):
        # Create resource model with fields
        wizard = self.env['generic.resource.type.wizard.create'].create({
            'name': 'Test Resource Model',
            'model': 'x_test_resource_model',
            'enable_chatter': True,
            'enable_mail_activity': True,
        })
        wizard.action_do_create_resource_type()
        resource_model = self.env['ir.model'].search([
            ('model', '=', wizard.model)])
        tree_view = resource_model.view_ids.filtered(
            lambda x: x.type == 'tree')

        field_char = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_char',
            'field_description': 'Field Char',
            'ttype': 'char',
            'resource_type_id': resource_model.resource_type_id.id
        })

        field_int = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_int',
            'field_description': 'Field Integer',
            'ttype': 'integer',
            'resource_type_id': resource_model.resource_type_id.id
        })
        field_bool = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_bool',
            'field_description': 'Field Boolean',
            'ttype': 'boolean',
            'resource_type_id': resource_model.resource_type_id.id
        })
        field_date = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_date',
            'field_description': 'Field Date',
            'ttype': 'date',
            'resource_type_id': resource_model.resource_type_id.id
        })
        field_float = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_float',
            'field_description': 'Field Float',
            'ttype': 'float',
            'resource_type_id': resource_model.resource_type_id.id
        })

        # Test create fields tree order
        self.env['generic.resource.type.view.tree.field.position'].create(
            [{'resource_type_id': resource_model.resource_type_id.id,
              'custom_field_id': field_char.id,
              'sequence': 5},
             {'resource_type_id': resource_model.resource_type_id.id,
              'custom_field_id': field_int.id,
              'sequence': 4},
             {'resource_type_id': resource_model.resource_type_id.id,
              'custom_field_id': field_bool.id,
              'sequence': 3},
             {'resource_type_id': resource_model.resource_type_id.id,
              'custom_field_id': field_date.id,
              'sequence': 2},
             {'resource_type_id': resource_model.resource_type_id.id,
              'custom_field_id': field_float.id,
              'sequence': 1}])
        # Expected fields order tree
        # +-----+-------------------------------+
        # |  0  |         x_name(n/a)           |
        # +-----+-------------------------------+
        # |  1  |       resource_id(n/a)        |
        # +-----+-------------------------------+
        # |  2  |    resource_visibility(n/a)   |
        # +-----+-------------------------------+
        # |  3  |         x_field_float(1)      |
        # +-----+-------------------------------+
        # |  4  |         x_field_date(2)       |
        # +-----+-------------------------------+
        # |  5  |          x_field_bool(3)      |
        # +-----+-------------------------------+
        # |  6  |          x_field_int(4)       |
        # +-----+-------------------------------+
        # |  7  |          x_field_char(5)      |
        # +-----+-------------------------------+

        fields_tree_order_dict = get_fields_order_in_parent_from_arch(
            arch=tree_view.arch)
        self.assertTrue(fields_tree_order_dict)
        self.assertEqual(field_char.tree_position_ids.sequence, 5)
        self.assertEqual(field_int.tree_position_ids.sequence, 4)
        self.assertEqual(field_bool.tree_position_ids.sequence, 3)
        self.assertEqual(field_date.tree_position_ids.sequence, 2)
        self.assertEqual(field_float.tree_position_ids.sequence, 1)
        self.assertEqual(fields_tree_order_dict.get(field_char.name), 7)
        self.assertEqual(fields_tree_order_dict.get(field_int.name), 6)
        self.assertEqual(fields_tree_order_dict.get(field_bool.name), 5)
        self.assertEqual(fields_tree_order_dict.get(field_date.name), 4)
        self.assertEqual(fields_tree_order_dict.get(field_float.name), 3)

        # Try to change field positions
        field_char_tree_position = self.env[
            'generic.resource.type.view.tree.field.position'].search(
            [('custom_field_id', '=', field_char.id)])
        field_float_tree_position = self.env[
            'generic.resource.type.view.tree.field.position'].search(
            [('custom_field_id', '=', field_float.id)])
        field_char_tree_position.sequence = 1
        field_float_tree_position.sequence = 5
        self.assertEqual(field_char.tree_position_ids.sequence, 1)
        self.assertEqual(field_float.tree_position_ids.sequence, 5)

        # Expected fields order tree
        # +-----+-------------------------------+
        # |  0  |         x_name(n/a)           |
        # +-----+-------------------------------+
        # |  1  |       resource_id(n/a)        |
        # +-----+-------------------------------+
        # |  2  |    resource_visibility(n/a)   |
        # +-----+-------------------------------+
        # |  3  |         x_field_char(1)       |
        # +-----+-------------------------------+
        # |  4  |         x_field_date(2)       |
        # +-----+-------------------------------+
        # |  5  |          x_field_bool(3)      |
        # +-----+-------------------------------+
        # |  6  |          x_field_int(4)       |
        # +-----+-------------------------------+
        # |  7  |          x_field_float(5)     |
        # +-----+-------------------------------+

        fields_tree_order = get_fields_order_in_parent_from_arch(
            arch=tree_view.arch)
        self.assertTrue(fields_tree_order)
        self.assertEqual(field_char.tree_position_ids.sequence, 1)
        self.assertEqual(field_int.tree_position_ids.sequence, 4)
        self.assertEqual(field_bool.tree_position_ids.sequence, 3)
        self.assertEqual(field_date.tree_position_ids.sequence, 2)
        self.assertEqual(field_float.tree_position_ids.sequence, 5)
        self.assertEqual(fields_tree_order.get(field_char.name), 3)
        self.assertEqual(fields_tree_order.get(field_int.name), 6)
        self.assertEqual(fields_tree_order.get(field_bool.name), 5)
        self.assertEqual(fields_tree_order.get(field_date.name), 4)
        self.assertEqual(fields_tree_order.get(field_float.name), 7)

        # Check field no more present in view after deleting
        field_char.unlink()
        self.assertFalse(field_char.exists())
        fields_tree_order = get_fields_order_in_parent_from_arch(
            arch=tree_view.arch)
        self.assertFalse(fields_tree_order.get('x_field_char'))

        # Check position record also deleted
        self.assertFalse(field_char_tree_position.exists())

    def test_form_fields_positions(self):
        # Create resource model with fields
        wizard = self.env['generic.resource.type.wizard.create'].create({
            'name': 'Test Resource Model',
            'model': 'x_test_resource_model',
            'enable_chatter': True,
            'enable_mail_activity': True,
        })
        wizard.action_do_create_resource_type()
        resource_model = self.env['ir.model'].search([
            ('model', '=', wizard.model)])
        form_view = resource_model.view_ids.filtered(
            lambda x: x.type == 'form')

        field_char = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_char',
            'field_description': 'Field Char',
            'ttype': 'char',
            'resource_type_id': resource_model.resource_type_id.id
        })

        field_int = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_int',
            'field_description': 'Field Integer',
            'ttype': 'integer',
            'resource_type_id': resource_model.resource_type_id.id
        })
        field_bool = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_bool',
            'field_description': 'Field Boolean',
            'ttype': 'boolean',
            'resource_type_id': resource_model.resource_type_id.id
        })
        field_date = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_date',
            'field_description': 'Field Date',
            'ttype': 'date',
            'resource_type_id': resource_model.resource_type_id.id
        })
        field_float = self.env['generic.resource.type.custom.field'].create({
            'name': 'x_field_float',
            'field_description': 'Field Float',
            'ttype': 'float',
            'resource_type_id': resource_model.resource_type_id.id
        })

        # Expected fields order form
        # The fields 'x_name', 'resource_id', 'resource_visibility'
        # are not custom fields. They have own order position that setted up
        # by creating. Thus they have not tree_sequence and
        # form_sequence and can not change own tree and form position.
        # In these tests their sequences are labeled as n/a
        # _______________________________________
        # |     |    Left Group    | Right Group |
        # +-----+------------------+-------------+
        # |  0  |     x_name(n/a)  |             |
        # +-----+------------------+-------------+
        # |  1  | resource_id(n/a) |             |
        # +-----+------------------+-------------+
        # |  2  |  x_field_char(0) |             |
        # +-----+------------------+-------------+
        # |  3  | x_field_int(0)   |             |
        # +-----+------------------+-------------+
        # |  4  | x_field_bool(0)  |             |
        # +-----+------------------+-------------+
        # |  5  | x_field_date(0)  |             |
        # +-----+------------------+-------------+
        # |  6  | x_field_float(0) |             |
        # +-----+------------------+-------------+

        fields_order_right = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_right"]')
        self.assertFalse(fields_order_right)
        fields_order_left = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_left"]')

        # No custom fields placed on form,
        # so we have only 'x_name' and 'resource_id' fields
        self.assertTrue(fields_order_left)
        self.assertEqual(fields_order_left.get('x_name'), 0)
        self.assertEqual(fields_order_left.get('resource_id'), 1)

        # Test change fields form order
        self.env['generic.resource.type.view.form.field.position'].create(
            [{'resource_type_id': resource_model.resource_type_id.id,
              'custom_field_id': field_char.id,
              'place_on_form': 'left_slot',
              'sequence': 5},
             {'resource_type_id': resource_model.resource_type_id.id,
              'custom_field_id': field_int.id,
              'place_on_form': 'left_slot',
              'sequence': 4},
             {'resource_type_id': resource_model.resource_type_id.id,
              'custom_field_id': field_date.id,
              'place_on_form': 'left_slot',
              'sequence': 2}])
        field_bool_form_position = self.env[
            'generic.resource.type.view.form.field.position'].create(
            {'resource_type_id': resource_model.resource_type_id.id,
             'custom_field_id': field_bool.id,
             'place_on_form': 'left_slot',
             'sequence': 3})
        field_float_form_position = self.env[
            'generic.resource.type.view.form.field.position'].create(
            {'resource_type_id': resource_model.resource_type_id.id,
             'custom_field_id': field_float.id,
             'place_on_form': 'left_slot',
             'sequence': 1})

        # Expected fields order form
        # _______________________________________
        # |     |    Left Group    | Right Group |
        # +-----+------------------+-------------+
        # |  0  |     x_name(n/a)  |             |
        # +-----+------------------+-------------+
        # |  1  | resource_id(n/a) |             |
        # +-----+------------------+-------------+
        # |  2  | x_field_float(1) |             |
        # +-----+------------------+-------------+
        # |  3  | x_field_date(2)  |             |
        # +-----+------------------+-------------+
        # |  4  | x_field_bool(3)  |             |
        # +-----+------------------+-------------+
        # |  5  |   x_field_int(4) |             |
        # +-----+------------------+-------------+
        # |  6  |  x_field_char(5) |             |
        # +-----+------------------+-------------+
        fields_order_right = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_right"]')
        self.assertFalse(fields_order_right)
        fields_order_left = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_left"]')
        self.assertTrue(fields_order_left)
        self.assertEqual(field_char.form_position_ids.sequence, 5)
        self.assertEqual(field_int.form_position_ids.sequence, 4)
        self.assertEqual(field_bool.form_position_ids.sequence, 3)
        self.assertEqual(field_date.form_position_ids.sequence, 2)
        self.assertEqual(field_float.form_position_ids.sequence, 1)
        self.assertEqual(fields_order_left.get(field_char.name), 6)
        self.assertEqual(fields_order_left.get(field_int.name), 5)
        self.assertEqual(fields_order_left.get(field_bool.name), 4)
        self.assertEqual(fields_order_left.get(field_date.name), 3)
        self.assertEqual(fields_order_left.get(field_float.name), 2)

        # Try to move fields to another group
        field_bool_form_position.place_on_form = 'right_slot'
        field_float_form_position.place_on_form = 'right_slot'
        # Expected fields order form
        # ______________________________________________
        # |     |    Left Group    |     Right Group   |
        # +-----+------------------+-------------------+
        # |  0  |   x_name(n/a)    | x_field_float(1)  |
        # +-----+------------------+-------------------+
        # |  1  | resource_id(n/a) |  x_field_bool(3)  |
        # +-----+------------------+-------------------+
        # |  2  |  x_field_date(2) |                   |
        # +-----+------------------+-------------------+
        # |  3  |  x_field_int(4)  |                   |
        # +-----+------------------+-------------------+
        # |  4  | x_field_char(5)  |                   |
        # +-----+------------------+-------------------+
        # |  5  |                  |                   |
        # +-----+------------------+-------------------+
        # |  6  |                  |                   |
        # +-----+------------------+-------------------+

        self.assertEqual(field_char.form_position_ids.sequence, 5)
        self.assertEqual(field_int.form_position_ids.sequence, 4)
        self.assertEqual(field_bool.form_position_ids.sequence, 3)
        self.assertEqual(field_date.form_position_ids.sequence, 2)
        self.assertEqual(field_float.form_position_ids.sequence, 1)

        # Check left group field positions
        fields_order_left = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_left"]')
        self.assertEqual(len(fields_order_left), 5)
        self.assertEqual(fields_order_left.get(field_char.name), 4)
        self.assertEqual(fields_order_left.get(field_int.name), 3)
        # field_bool no more in left group
        self.assertIsNone(fields_order_left.get(field_bool.name))
        self.assertEqual(fields_order_left.get(field_date.name), 2)
        # field_float no more in left group
        self.assertIsNone(fields_order_left.get(field_float.name))

        # Check right group field positions
        fields_order_right = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_right"]')
        self.assertEqual(len(fields_order_right), 2)
        self.assertEqual(fields_order_right.get(field_float.name), 0)
        self.assertEqual(fields_order_right.get(field_bool.name), 1)

        # Try to change field form sequences
        field_char_form_position = self.env[
            'generic.resource.type.view.form.field.position'].search(
            [('custom_field_id', '=', field_char.id)])
        field_float_form_position = self.env[
            'generic.resource.type.view.form.field.position'].search(
            [('custom_field_id', '=', field_float.id)])
        field_char_form_position.sequence = 1
        field_float_form_position.sequence = 5
        self.assertEqual(field_char.form_position_ids.sequence, 1)
        self.assertEqual(field_float.form_position_ids.sequence, 5)
        # Expected fields order form
        # ______________________________________________
        # |     |    Left Group    |     Right Group   |
        # +-----+------------------+-------------------+
        # |  0  |   x_name(n/a)    |   x_field_bool(3) |
        # +-----+------------------+-------------------+
        # |  1  | resource_id(n/a) |  x_field_float(5) |
        # +-----+------------------+-------------------+
        # |  2  |  x_field_char(1) |                   |
        # +-----+------------------+-------------------+
        # |  3  |  x_field_date(2) |                   |
        # +-----+------------------+-------------------+
        # |  4  |   x_field_int(4) |                   |
        # +-----+------------------+-------------------+
        # |  5  |                  |                   |
        # +-----+------------------+-------------------+
        # |  6  |                  |                   |
        # +-----+------------------+-------------------+

        self.assertEqual(field_char.form_position_ids.sequence, 1)
        self.assertEqual(field_int.form_position_ids.sequence, 4)
        self.assertEqual(field_bool.form_position_ids.sequence, 3)
        self.assertEqual(field_date.form_position_ids.sequence, 2)
        self.assertEqual(field_float.form_position_ids.sequence, 5)

        # Check left group field positions
        fields_order_left = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_left"]')
        self.assertEqual(len(fields_order_left), 5)
        self.assertEqual(fields_order_left.get(field_char.name), 2)
        self.assertEqual(fields_order_left.get(field_int.name), 4)
        self.assertEqual(fields_order_left.get(field_date.name), 3)

        # Check right group field positions
        fields_order_right = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_right"]')
        self.assertEqual(len(fields_order_right), 2)
        self.assertEqual(fields_order_right.get(field_float.name), 1)
        self.assertEqual(fields_order_right.get(field_bool.name), 0)

        # Check unlink custom field
        field_char_ir_model = field_char.ir_model_custom_field_id
        field_char.unlink()
        # Ensure custom field deleted
        self.assertFalse(field_char.exists())
        fields_order_left = get_fields_order_in_parent_from_arch(
            arch=form_view.arch, parent='.//group[@name="group_info_left"]')
        # Ensure field not present in view
        self.assertFalse(fields_order_left.get('x_field_char'))
        # Ensure related ir model field deleted
        self.assertFalse(field_char_ir_model.exists())
        # Check field position also deleted
        self.assertFalse(field_char_form_position.exists())
