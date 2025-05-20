from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("-at_install", "post_install")
class TestAccessRights(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccessRights, cls).setUpClass()

        # Groups
        cls.group_resource_user_implicit = cls.env.ref(
            'generic_resource.group_generic_resource_user_implicit')
        cls.group_resource_user = cls.env.ref(
            'generic_resource.group_generic_resource_user')
        cls.group_resource_manager = cls.env.ref(
            'generic_resource.group_generic_resource_manager')
        cls.group_system = cls.env.ref(
            'base.group_system')
        cls.group_portal = cls.env.ref(
            'base.group_portal')
        cls.group_public = cls.env.ref(
            'base.group_public')

        # Users
        cls.resource_user_implicit = cls.env.ref(
            'generic_resource_type_builder.demo_resource_user_implicit')
        cls.resource_user = cls.env.ref(
            'generic_resource_type_builder.demo_resource_user')
        cls.resource_manager = cls.env.ref(
            'generic_resource_type_builder.demo_resource_manager')
        cls.user_admin = cls.env.ref(
            'base.user_admin')
        cls.portal_user = cls.env.ref(
            'base.demo_user0')
        cls.public_user = cls.env.ref(
            'base.public_user')

        # Envs
        cls.uienv = cls.env(  # pylint: disable=not-callable
            user=cls.resource_user_implicit)
        cls.uenv = cls.env(  # pylint: disable=not-callable
            user=cls.resource_user)
        cls.menv = cls.env(  # pylint: disable=not-callable
            user=cls.resource_manager)
        cls.aenv = cls.env(  # pylint: disable=not-callable
            user=cls.user_admin)
        cls.penv = cls.env(  # pylint: disable=not-callable
            user=cls.portal_user)
        cls.pubenv = cls.env(  # pylint: disable=not-callable
            user=cls.public_user)

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_access_rights_wizard(self):
        # Check resource user implicit has correct group
        self.assertIn(
            self.group_resource_user_implicit,
            self.resource_user_implicit.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_user_implicit.groups_id)
        # Try to create wizard with resource user implicit
        with self.assertRaises(AccessError):
            self.uienv['generic.resource.type.wizard.create'].create({
                'name': 'Test Resource Model',
                'model': 'x_test_resource_access_model',
                'enable_chatter': True,
                'enable_mail_activity': True,
            }).action_do_create_resource_type()

        # Check resource user has correct group
        self.assertIn(
            self.group_resource_user,
            self.resource_user.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_user.groups_id)
        # Try to create wizard with resource user
        with self.assertRaises(AccessError):
            self.uenv['generic.resource.type.wizard.create'].create({
                'name': 'Test Resource Model',
                'model': 'x_test_resource_access_model',
                'enable_chatter': True,
                'enable_mail_activity': True,
            }).action_do_create_resource_type()

        # Check resource manager has correct group
        self.assertIn(
            self.group_resource_manager,
            self.resource_manager.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_manager.groups_id)
        # Try to create wizard with resource manager
        with self.assertRaises(AccessError):
            self.menv['generic.resource.type.wizard.create'].create({
                'name': 'Test Resource Model',
                'model': 'x_test_resource_access_model',
                'enable_chatter': True,
                'enable_mail_activity': True,
            }).action_do_create_resource_type()

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_access_rights_resource_model(self):
        self.env['generic.resource.type.wizard.create'].create({
            'name': 'Test Resource Model',
            'model': 'x_test_resource_access_model',
            'enable_chatter': True,
            'enable_mail_activity': True,
        }).action_do_create_resource_type()
        resource_model = self.env['ir.model'].search([
            ('model', '=', 'x_test_resource_access_model')])
        self.assertTrue(resource_model)

        # Check resource user implicit has correct group
        self.assertIn(
            self.group_resource_user_implicit,
            self.resource_user_implicit.groups_id)
        # Check rights resource user implicit
        self.uienv[resource_model.model].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.uienv[resource_model.model].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.uienv[resource_model.model].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.uienv[resource_model.model].check_access_rights('unlink')

        # Check resource user has correct group
        self.assertIn(
            self.group_resource_user,
            self.resource_user.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_user.groups_id)
        # Check rights resource user
        self.uenv[resource_model.model].check_access_rights('read')
        self.uenv[resource_model.model].check_access_rights('write')
        self.uenv[resource_model.model].check_access_rights('create')
        self.uenv[resource_model.model].check_access_rights('unlink')

        # Check resource manager has correct group
        self.assertIn(
            self.group_resource_manager,
            self.resource_manager.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_manager.groups_id)
        # Check rights resource manager
        self.menv[resource_model.model].check_access_rights('read')
        self.menv[resource_model.model].check_access_rights('write')
        self.menv[resource_model.model].check_access_rights('create')
        self.menv[resource_model.model].check_access_rights('unlink')

        # Check portal user correct group
        self.assertIn(
            self.group_portal,
            self.portal_user.groups_id)
        # Check rights portal user
        self.penv[resource_model.model].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.penv[resource_model.model].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.penv[resource_model.model].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.penv[resource_model.model].check_access_rights('unlink')

        # Check public user correct group
        self.assertIn(
            self.group_public,
            self.public_user.groups_id)
        # Check rights public user
        self.pubenv[resource_model.model].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.pubenv[resource_model.model].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.pubenv[resource_model.model].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.pubenv[resource_model.model].check_access_rights('unlink')

        # Delete created views
        resource_model.view_ids.unlink()

        # Delete created model
        resource_model.with_context(_force_unlink=True).unlink()

        # Ensure model removed
        self.assertFalse(resource_model.exists())

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_access_rights_custom_field(self):
        # Create model with field from admin env
        # Check admin has correct group
        self.assertIn(
            self.group_system,
            self.user_admin.groups_id)
        self.aenv['generic.resource.type.wizard.create'].create({
            'name': 'Test Resource Model',
            'model': 'x_test_resource_access_model',
            'enable_chatter': True,
            'enable_mail_activity': True,
        }).action_do_create_resource_type()
        resource_model = self.env['ir.model'].search([
            ('model', '=', 'x_test_resource_access_model')])
        self.assertTrue(resource_model.exists())
        # Try to create custom field with resource user implicit
        with self.assertRaises(AccessError):
            self.uienv['generic.resource.type.custom.field'].create({
                'name': 'x_field_char',
                'field_description': 'Field Char',
                'ttype': 'char',
                'resource_type_id': resource_model.resource_type_id.id
            })
        # Try to create custom field with resource user
        with self.assertRaises(AccessError):
            self.uenv['generic.resource.type.custom.field'].create({
                'name': 'x_field_char',
                'field_description': 'Field Char',
                'ttype': 'char',
                'resource_type_id': resource_model.resource_type_id.id
            })
        # Try to create custom field with resource manager
        with self.assertRaises(AccessError):
            self.menv['generic.resource.type.custom.field'].create({
                'name': 'x_field_char',
                'field_description': 'Field Char',
                'ttype': 'char',
                'resource_type_id': resource_model.resource_type_id.id
            })

        # Create custom field with system user
        field_char = self.aenv['generic.resource.type.custom.field'].create({
            'name': 'x_field_char',
            'field_description': 'Field Char',
            'ttype': 'char',
            'resource_type_id': resource_model.resource_type_id.id
        })
        self.assertTrue(field_char.exists())

        # Check resource user implicit has correct group
        self.assertIn(
            self.group_resource_user_implicit,
            self.resource_user_implicit.groups_id)
        # Check rights resource user implicit
        with self.assertRaises(AccessError):
            self.uienv[field_char._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.uienv[field_char._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.uienv[field_char._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.uienv[field_char._name].check_access_rights('unlink')

        # Check resource user has correct group
        self.assertIn(
            self.group_resource_user,
            self.resource_user.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_user.groups_id)
        # Check rights resource user
        with self.assertRaises(AccessError):
            self.uenv[field_char._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.uenv[field_char._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.uenv[field_char._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.uenv[field_char._name].check_access_rights('unlink')

        # Check resource manager has correct group
        self.assertIn(
            self.group_resource_manager,
            self.resource_manager.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_manager.groups_id)
        # Check rights resource manager
        self.menv[field_char._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.menv[field_char._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.menv[field_char._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.menv[field_char._name].check_access_rights('unlink')

        # Check user admin has correct group
        self.assertIn(
            self.group_system,
            self.user_admin.groups_id)
        # Check rights user admin
        self.aenv[field_char._name].check_access_rights('read')
        self.aenv[field_char._name].check_access_rights('write')
        self.aenv[field_char._name].check_access_rights('create')
        self.aenv[field_char._name].check_access_rights('unlink')

        # Delete created views
        resource_model.view_ids.unlink()

        # Delete created model
        resource_model.with_context(_force_unlink=True).unlink()

        # Ensure model removed
        self.assertFalse(resource_model.exists())

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_access_rights_tree_position(self):
        # Create init data for tests
        # Create model
        self.aenv['generic.resource.type.wizard.create'].create({
            'name': 'Test Resource Model',
            'model': 'x_test_resource_access_model',
            'enable_chatter': True,
            'enable_mail_activity': True,
        }).action_do_create_resource_type()
        resource_model = self.env['ir.model'].search([
            ('model', '=', 'x_test_resource_access_model')])
        self.assertTrue(resource_model.exists())
        # Create custom field
        field_char = self.aenv['generic.resource.type.custom.field'].create({
            'name': 'x_field_char',
            'field_description': 'Field Char',
            'ttype': 'char',
            'resource_type_id': resource_model.resource_type_id.id
        })
        self.assertTrue(field_char.exists())

        # Try to create tree position for field with resource user implicit
        with self.assertRaises(AccessError):
            self.uienv[
                'generic.resource.type.view.tree.field.position'].create({
                    'resource_type_id': resource_model.resource_type_id.id,
                    'custom_field_id': field_char.id,
                    'sequence': 5})
        # Try to create tree position for field with resource user
        with self.assertRaises(AccessError):
            self.uenv[
                'generic.resource.type.view.tree.field.position'].create({
                    'resource_type_id': resource_model.resource_type_id.id,
                    'custom_field_id': field_char.id,
                    'sequence': 5})
        # Try to create tree position for field with resource manager
        with self.assertRaises(AccessError):
            self.menv[
                'generic.resource.type.view.tree.field.position'].create({
                    'resource_type_id': resource_model.resource_type_id.id,
                    'custom_field_id': field_char.id,
                    'sequence': 5})

        # Create custom tree position for field with system user
        field_char_tree_position = self.aenv[
            'generic.resource.type.view.tree.field.position'].create({
                'resource_type_id': resource_model.resource_type_id.id,
                'custom_field_id': field_char.id,
                'sequence': 5})
        self.assertTrue(field_char_tree_position.exists())

        # Check resource user implicit has correct group
        self.assertIn(
            self.group_resource_user_implicit,
            self.resource_user_implicit.groups_id)
        # Check rights resource user implicit
        with self.assertRaises(AccessError):
            self.uienv[
                field_char_tree_position._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.uienv[
                field_char_tree_position._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.uienv[
                field_char_tree_position._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.uienv[
                field_char_tree_position._name].check_access_rights('unlink')

        # Check resource user has correct group
        self.assertIn(
            self.group_resource_user,
            self.resource_user.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_user.groups_id)
        # Check rights resource user
        with self.assertRaises(AccessError):
            self.uenv[
                field_char_tree_position._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.uenv[
                field_char_tree_position._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.uenv[
                field_char_tree_position._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.uenv[
                field_char_tree_position._name].check_access_rights('unlink')

        # Check resource manager has correct group
        self.assertIn(
            self.group_resource_manager,
            self.resource_manager.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_manager.groups_id)
        # Check rights resource manager
        self.menv[field_char_tree_position._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.menv[
                field_char_tree_position._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.menv[
                field_char_tree_position._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.menv[
                field_char_tree_position._name].check_access_rights('unlink')

        # Check user admin has correct group
        self.assertIn(
            self.group_system,
            self.user_admin.groups_id)
        # Check rights user admin
        self.aenv[field_char_tree_position._name].check_access_rights('read')
        self.aenv[field_char_tree_position._name].check_access_rights('write')
        self.aenv[field_char_tree_position._name].check_access_rights('create')
        self.aenv[field_char_tree_position._name].check_access_rights('unlink')

        # Delete created views
        resource_model.view_ids.unlink()

        # Delete created model
        resource_model.with_context(_force_unlink=True).unlink()

        # Ensure model removed
        self.assertFalse(resource_model.exists())

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_access_rights_form_position(self):
        # Create init data for tests
        # Create model
        self.aenv['generic.resource.type.wizard.create'].create({
            'name': 'Test Resource Model',
            'model': 'x_test_resource_access_model',
            'enable_chatter': True,
            'enable_mail_activity': True,
        }).action_do_create_resource_type()
        resource_model = self.env['ir.model'].search([
            ('model', '=', 'x_test_resource_access_model')])
        self.assertTrue(resource_model.exists())
        # Create custom field
        field_char = self.aenv[
            'generic.resource.type.custom.field'].create({
                'name': 'x_field_char',
                'field_description': 'Field Char',
                'ttype': 'char',
                'resource_type_id': resource_model.resource_type_id.id})
        self.assertTrue(field_char.exists())

        # Try to create form position for field with resource user implicit
        with self.assertRaises(AccessError):
            self.uienv[
                'generic.resource.type.view.form.field.position'].create({
                    'resource_type_id': resource_model.resource_type_id.id,
                    'custom_field_id': field_char.id,
                    'place_on_form': 'left_slot',
                    'sequence': 5})
        # Try to create form position for field with resource user
        with self.assertRaises(AccessError):
            self.uenv[
                'generic.resource.type.view.form.field.position'].create({
                    'resource_type_id': resource_model.resource_type_id.id,
                    'custom_field_id': field_char.id,
                    'place_on_form': 'left_slot',
                    'sequence': 5})
        # Try to create form position for field with resource manager
        with self.assertRaises(AccessError):
            self.menv[
                'generic.resource.type.view.form.field.position'].create({
                    'resource_type_id': resource_model.resource_type_id.id,
                    'custom_field_id': field_char.id,
                    'place_on_form': 'left_slot',
                    'sequence': 5})

        # Create form position for field with system user
        field_char_form_position = self.aenv[
            'generic.resource.type.view.form.field.position'].create({
                'resource_type_id': resource_model.resource_type_id.id,
                'custom_field_id': field_char.id,
                'place_on_form': 'left_slot',
                'sequence': 5})
        self.assertTrue(field_char_form_position.exists())

        # Check resource user implicit has correct group
        self.assertIn(
            self.group_resource_user_implicit,
            self.resource_user_implicit.groups_id)
        # Check rights resource user implicit
        with self.assertRaises(AccessError):
            self.uienv[
                field_char_form_position._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.uienv[
                field_char_form_position._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.uienv[
                field_char_form_position._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.uienv[
                field_char_form_position._name].check_access_rights('unlink')

        # Check resource user has correct group
        self.assertIn(
            self.group_resource_user,
            self.resource_user.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_user.groups_id)
        # Check rights resource user
        with self.assertRaises(AccessError):
            self.uenv[
                field_char_form_position._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.uenv[
                field_char_form_position._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.uenv[
                field_char_form_position._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.uenv[
                field_char_form_position._name].check_access_rights('unlink')

        # Check resource manager has correct group
        self.assertIn(
            self.group_resource_manager,
            self.resource_manager.groups_id)
        self.assertNotIn(
            self.env.ref('base.group_system'),
            self.resource_manager.groups_id)
        # Check rights resource manager
        self.menv[field_char_form_position._name].check_access_rights('read')
        with self.assertRaises(AccessError):
            self.menv[
                field_char_form_position._name].check_access_rights('write')
        with self.assertRaises(AccessError):
            self.menv[
                field_char_form_position._name].check_access_rights('create')
        with self.assertRaises(AccessError):
            self.menv[
                field_char_form_position._name].check_access_rights('unlink')

        # Check user admin has correct group
        self.assertIn(
            self.group_system,
            self.user_admin.groups_id)
        # Check rights user admin
        self.aenv[field_char_form_position._name].check_access_rights('read')
        self.aenv[field_char_form_position._name].check_access_rights('write')
        self.aenv[field_char_form_position._name].check_access_rights('create')
        self.aenv[field_char_form_position._name].check_access_rights('unlink')

        # Delete created views
        resource_model.view_ids.unlink()

        # Delete created model
        resource_model.with_context(_force_unlink=True).unlink()

        # Ensure model removed
        self.assertFalse(resource_model.exists())
