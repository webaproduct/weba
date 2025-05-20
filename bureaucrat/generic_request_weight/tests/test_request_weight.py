from dateutil.relativedelta import relativedelta
from lxml import etree  # nosec

from odoo import fields
from odoo.tests.common import TransactionCase, tagged, Form
from odoo.addons.generic_mixin.tests.common import (
    ReduceLoggingMixin,
)
from odoo.addons.generic_request.tests.common import (
    freeze_time,
    RequestClassifierUtilsMixin)


def get_field_attrs_from_arch(arch, field_name):
    """Extract the attributes of a specific field from an XML architecture.

    Args:
        arch (str): A string representation of the XML architecture.
        field_name (str): The name of the field whose attributes
        should be extracted.

    Returns:
        dict or False: A dictionary containing the attributes
        of the specified field, where the keys are the attribute names
        and the values are the attribute values.
        Returns False if the field is not found.

    Example:
        arch = '<form><field name="foo" type="char" size="64"/></form>'
        get_field_attrs_from_arch(arch, 'foo')
        {'name': 'foo', 'type': 'char', 'size': '64'}
    """
    arch_field = etree.fromstring(arch).find(  # nosec
        ".//field[@name='%s']" % field_name)
    if arch_field is not None:
        return dict(arch_field.attrib)
    return False


@tagged("-at_install", "post_install")
class TestRequestWeightOrder(ReduceLoggingMixin,
                             RequestClassifierUtilsMixin,
                             TransactionCase):
    # pylint: disable=pointless-string-statement

    @classmethod
    def setUpClass(cls):
        super(TestRequestWeightOrder, cls).setUpClass()
        # Services
        cls.test_service = cls.env.ref(
            'generic_service.generic_service_default')

        # Service Levels
        cls.test_service_level1 = cls.env.ref(
            'generic_service.generic_service_level_1')
        cls.test_service_level2 = cls.env.ref(
            'generic_service.generic_service_level_2')

        # Categories
        cls.test_category = cls.env.ref(
            'generic_request.request_category_demo_technical_configuration')
        cls.sla_category = cls.env.ref(
            'generic_request.request_category_demo_general')

        # Types
        cls.test_type = cls.env.ref('generic_request.request_type_sequence')
        cls.sla_type = cls.env.ref(
            'generic_request_sla.request_type_sla_complex')

        # Stages
        cls.sla_stage_new = cls.env.ref(
            'generic_request_sla.request_stage_type_sla_complex_new')
        cls.sla_stage_progress = cls.env.ref(
            'generic_request_sla.request_stage_type_sla_complex_in_progress')
        cls.sla_stage_completed = cls.env.ref(
            'generic_request_sla.request_stage_type_sla_complex_completed')
        cls.stage_new = cls.env.ref(
            'generic_request.request_stage_type_sequence_new')
        cls.stage_sent = cls.env.ref(
            'generic_request.request_stage_type_sequence_sent')

        # SLA Rule
        cls.sla_rule2h_reaction = cls.env.ref(
            'generic_request_sla.request_sla_rule_reaction_time_2h')
        cls.sla_rule8h_resolution = cls.env.ref(
            'generic_request_sla.request_sla_rule_resolution_time_8h')

        # Users, Partners, Groups
        cls.test_author = cls.env.ref('base.res_partner_address_15')
        cls.demo_user = cls.env.ref('base.user_demo')
        cls.group_request_manager = cls.env.ref(
            'generic_request.group_request_manager')
        cls.group_request_user = cls.env.ref(
            'generic_request.group_request_user')

        # In case if this test will be running, when some request actions
        # registered, then we have to disable them, because this test do
        # not expect existing automated actions.
        # Especially when it installed together with test_generic_request,
        # that defines actions that create new mail activities on SLA
        # warnings and failures
        if 'request.event.action' in cls.env:
            cls.env['request.event.action'].search([]).write({'active': False})

    def test_request_weight_defaults(self):
        # Check default computation of request weight
        Request = self.env['request.request']
        self.test_author.parent_id.write({
            'service_level_id': self.test_service_level1.id
        })

        # Create request
        request = Request.create({
            'name': 'Test Request',
            'service_id': self.test_service.id,
            'category_id': self.test_category.id,
            'type_id': self.test_type.id,
            'author_id': self.test_author.id,
            'request_text': 'Check Default weight'
        })
        # Check default weights of Service, Service Level,
        # Category, Type, Stage
        self.assertEqual(request.service_id.weight, 1.0)
        self.assertEqual(request.service_level_id, self.test_service_level1)
        self.assertEqual(request.service_level_id.weight, 1.0)
        self.assertEqual(request.category_id.weight, 1.0)
        self.assertEqual(request.type_id.weight, 2.0)
        self.assertEqual(request.stage_id.weight, 1.0)
        self.assertEqual(request.priority, '3')
        self.assertEqual(request.kanban_state, 'normal')
        self.assertFalse(request.sla_control_ids)
        self.assertFalse(request.activity_state)

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 1.0      | 20.0
        """
        self.assertEqual(request.weight, 20.0)

    def test_change_request_service_category_type(self):
        Request = self.env['request.request']

        test_category1 = self.env['request.category'].create({
            'name': 'Test Category 1',
            'code': 'test-category-1',
            'description': 'Test Category 1 Description',
            'weight': 4.0,
        })

        test_service1 = self.env['generic.service'].create({
            'name': 'Test Service 1',
            'code': 'test-service-1',
            'description': 'Test Service 1 description',
            'weight': 3.0,
        })

        self.ensure_classifier(
            service=test_service1,
            category=self.test_category,
            request_type=self.test_type)
        self.ensure_classifier(
            service=test_service1,
            category=test_category1,
            request_type=self.test_type)

        # Create request
        request = Request.create({
            'name': 'Test Request',
            'service_id': self.test_service.id,
            'category_id': self.test_category.id,
            'type_id': self.test_type.id,
            'author_id': self.test_author.id,
            'request_text': 'Check Service, Category, Type weight'
        })

        # Change request service
        request.service_id = test_service1
        self.assertEqual(request.service_id.weight, 3.0)
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        3.0     | 1.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 1.0      | 60.0
        """
        self.assertEqual(request.weight, 60.0)

        # Try to change weight of existing service
        test_service1.weight = 2.0
        self.assertEqual(request.service_id.weight, 2.0)
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        2.0     | 1.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 1.0      | 40.0
        """
        self.assertEqual(request.weight, 40.0)

        # Change request category
        request.category_id = test_category1
        self.assertEqual(request.category_id.weight, 4.0)
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        2.0     | 1.0           | 4.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 1.0      | 160.0
        """
        self.assertEqual(request.weight, 160.0)

        # Try to change weight of existing category
        test_category1.weight = 2.0
        self.assertEqual(request.category_id.weight, 2.0)
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        2.0     | 1.0           | 2.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 1.0      | 80.0
        """
        self.assertEqual(request.weight, 80.0)

        # Try to change weight of existing type
        self.test_type.weight = 10.0
        self.assertEqual(request.type_id.weight, 10.0)
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        2.0     | 1.0           | 2.0      | 10.0 | 1.0   | 1.0      | 1.0          | 10.0 | 1.0      | 400.0
        """
        self.assertEqual(request.weight, 400.0)

    def test_service_level_weight(self):
        Request = self.env['request.request']

        # Change SL2 weight and assign it to request author
        self.test_service_level2.weight = 3.0
        self.test_author.parent_id.write({
            'service_level_id': self.test_service_level2.id
        })

        # Create request
        request = Request.create({
            'name': 'Test Request',
            'service_id': self.test_service.id,
            'category_id': self.test_category.id,
            'type_id': self.test_type.id,
            'author_id': self.test_author.id,
            'request_text': 'Check service level weight'
        })

        self.assertEqual(request.service_level_id, self.test_service_level2)

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 3.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 1.0      | 60.0
        """
        self.assertEqual(request.weight, 60.0)

        # Change weight of SL
        self.test_service_level2.weight = 4.0

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 4.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 1.0      | 80.0
        """
        self.assertEqual(request.weight, 80.0)

    def test_request_stage_weight(self):
        Request = self.env['request.request']

        # Create request
        request = Request.create({
            'name': 'Test Request',
            'service_id': self.test_service.id,
            'category_id': self.test_category.id,
            'type_id': self.test_type.id,
            'author_id': self.test_author.id,
            'request_text': 'Check stage weight'
        })
        self.assertEqual(request.weight, 20.0)
        self.assertEqual(request.stage_id, self.stage_new)

        # Change current stage weight
        request.stage_id.weight = 5.0

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 5.0   | 1.0      | 1.0          | 10.0 | 1.0      | 100.0
        """
        self.assertEqual(request.weight, 100.0)

        # Change next request stage weight and move request to it
        self.stage_sent.weight = 4.0
        request.stage_id = self.stage_sent
        self.assertEqual(request.stage_id, self.stage_sent)

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 4.0   | 1.0      | 1.0          | 10.0 | 1.0      | 80.0
        """
        self.assertEqual(request.weight, 80.0)

    def test_priority_kanban_state_weight(self):
        Request = self.env['request.request']

        # Create request
        request = Request.create({
            'name': 'Test Request',
            'service_id': self.test_service.id,
            'category_id': self.test_category.id,
            'type_id': self.test_type.id,
            'author_id': self.test_author.id,
            'request_text': 'Check stage weight'
        })
        self.assertEqual(request.weight, 20.0)

        # Change priority to Lowest
        request.priority = '1'

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 10.0     | 1.0          | 10.0 | 1.0      | 200.0
        """
        self.assertEqual(request.weight, 200.0)

        # Change Kanban state to 'done'
        request.kanban_state = 'done'

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 10.0     | 0.01         | 10.0 | 1.0      | 2.0
        """
        self.assertEqual(request.weight, 2.0)

        # Change Kanban state to 'blocked'
        request.kanban_state = 'blocked'

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 10.0     | 10.0         | 10.0 | 1.0      | 2000.0
        """
        self.assertEqual(request.weight, 2000.0)

        # Change priority to Highest
        request.priority = '5'

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 0.0      | 10.0         | 10.0 | 1.0      | 0.0
        """
        self.assertEqual(request.weight, 0.0)

    def test_sla_weight(self):
        Request = self.env['request.request']
        # Fix compute time of SLA rules to test
        # in non-working time
        self.sla_rule2h_reaction.write({
            'compute_time': 'absolute',
            'sla_calendar_id': False,
        })
        self.sla_rule8h_resolution.write({
            'compute_time': 'absolute',
            'sla_calendar_id': False,
        })

        # Create SLA request
        with freeze_time('2020-05-03 7:00:00'):
            request = Request.create({
                'name': 'Test Request with SLA',
                'category_id': self.sla_category.id,
                'type_id': self.sla_type.id,
                'author_id': self.test_author.id,
                'request_text': 'Check weight SLA',
            })
        self.assertEqual(request.weight, 20.0)
        self.assertTrue(
            all([r.sla_state == 'ok' for r in request.sla_control_ids])
        )

        # Move request after 1h to produce sla warning
        with freeze_time('2020-05-03 8:30:00'):
            request.stage_id = self.sla_stage_progress
            request.user_id = self.demo_user
        self.assertTrue(
            'warning' in [r.sla_state for r in request.sla_control_ids]
        )

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 0.5  | 1.0       | 1.0
        """
        self.assertFalse(request.service_id)
        self.assertFalse(request.service_level_id)
        self.assertEqual(request.category_id.weight, 1.0)
        self.assertEqual(request.type_id.weight, 2.0)
        self.assertEqual(request.stage_id.weight, 1.0)
        self.assertEqual(request.priority, '3')
        self.assertEqual(request.kanban_state, 'normal')
        self.assertIn("warning", request.sla_control_ids.mapped('sla_state'))
        self.assertNotIn("failed", request.sla_control_ids.mapped('sla_state'))
        self.assertNotEqual(request.activity_state, 'overdue')
        self.assertNotEqual(request.activity_state, 'today')
        self.assertEqual(request.weight, 1.0)

        # Move request after 8h of resolution to produce sla fail
        with freeze_time('2020-05-03 17:00:00'):
            request.stage_id = self.sla_stage_completed
        self.assertTrue(
            'failed' in [r.sla_state for r in request.sla_control_ids]
        )

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 0.1  | 1.0       | 0.2
        """
        self.assertEqual(request.weight, 0.2)

    def test_activity_weight(self):
        Request = self.env['request.request']

        # Create request
        request = Request.create({
            'name': 'Test Request',
            'service_id': self.test_service.id,
            'category_id': self.test_category.id,
            'type_id': self.test_type.id,
            'author_id': self.test_author.id,
            'user_id': self.demo_user.id,
            'request_text': 'Check stage weight'
        })
        self.assertEqual(request.weight, 20.0)

        # Create Activity
        res_model = self.env['ir.model']._get(request._name)
        activity = self.env['mail.activity'].create({
            'res_model_id': res_model.id,
            'res_id': request.id,
            'summary': 'Test Activity',
            'activity_type_id':
                self.env.ref('mail.mail_activity_data_todo').id,
            'user_id': self.demo_user.id,
            'date_deadline': fields.Date.today()
        })
        request.invalidate_model(fnames=['activity_state', 'activity_ids'])
        self.assertEqual(request.activity_state, 'today')

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 0.5      | 10.0
        """
        self.assertEqual(request.weight, 10.0)

        # Change activity date to set state 'overdue'
        activity.write({
            'date_deadline': fields.Date.today() - relativedelta(days=1)})
        request.invalidate_recordset()
        self.assertEqual(request.activity_state, 'overdue')

        # Check weight of request
        """# noqa
        _____________________________________________________________________________________________________
        Service | Service Level | Category | Type | Stage | Priority | Kanban State | SLA  | Activity | TOTAL
        --------+---------------+----------+------+-------+----------+--------------+------+----------+------
        1.0     | 1.0           | 1.0      | 2.0  | 1.0   | 1.0      | 1.0          | 10.0 | 0.1      | 2.0
        """
        self.assertEqual(request.weight, 2.0)

    def test_order_direction(self):
        # Check default order
        default_date_order = 'DESC'
        self.assertEqual(
            self.env['ir.config_parameter'].get_param(
                'generic_request_weight.request_sort_direction', 'DESC'),
            default_date_order)

        expected_order = 'weight ASC, date_created DESC'
        list_requests = self.env['request.request'].search([]).mapped('id')
        expected_list_requests = self.env['request.request'].search(
            [], order=expected_order).mapped('id')
        self.assertListEqual(list_requests, expected_list_requests)

        # Change the date order direction in res.config.settings
        expected_order = 'weight ASC, date_created ASC'
        with Form(self.env['res.config.settings']) as form_settings:
            form_settings.request_date_related_sort_direction = 'ASC'

            # Using `.set_values()` here instead of `.execute()` because,
            # `.execute()` want to install or uninstall `base_import` module
            # for some reason. But `.set_values()` is enough for this test
            form_settings.save().set_values()  # .execute()

        self.assertEqual(
            self.env['ir.config_parameter'].get_param(
                'generic_request_weight.request_sort_direction'),
            'ASC')
        list_requests = self.env['request.request'].search([]).mapped('id')
        expected_list_requests = self.env['request.request'].search(
            [], order=expected_order).mapped('id')
        self.assertListEqual(list_requests, expected_list_requests)

    def test_access_rights(self):
        self.assertNotIn(self.group_request_manager, self.demo_user.groups_id)

        service_arch = self.env['generic.service'].with_user(
            self.demo_user).get_views(
            [(None, 'form')])['views']['form']['arch']
        sl_arch = self.env['generic.service.level'].with_user(
            self.demo_user).get_views(
            [(None, 'form')])['views']['form']['arch']
        category_arch = self.env['request.category'].with_user(
            self.demo_user).get_views(
            [(None, 'form')])['views']['form']['arch']
        type_arch = self.env['request.type'].with_user(
            self.demo_user).get_views(
            [(None, 'form')])['views']['form']['arch']
        stage_arch = self.env['request.stage'].with_user(
            self.demo_user).get_views(
            [(None, 'form')])['views']['form']['arch']

        self.assertFalse(get_field_attrs_from_arch(service_arch, 'weight'))
        self.assertFalse(get_field_attrs_from_arch(sl_arch, 'weight'))
        self.assertFalse(get_field_attrs_from_arch(category_arch, 'weight'))
        self.assertFalse(get_field_attrs_from_arch(type_arch, 'weight'))
        self.assertFalse(get_field_attrs_from_arch(stage_arch, 'weight'))
