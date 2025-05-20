# pylint: disable=too-many-lines
import logging
from psycopg2 import IntegrityError

from odoo import exceptions, fields
from odoo.tools.misc import mute_logger

from odoo.addons.generic_mixin.tests.common import deactivate_records_for_model

from odoo.tests.common import Form
from .common import RequestCase, freeze_time, get_utc_datetime
from ..models.request_request import html2text

_logger = logging.getLogger(__name__)


class TestRequestBase(RequestCase):
    """Test request base
    """

    def test_090_type_counters(self):
        access_type = self.env.ref(
            'generic_request.request_type_access')
        self.assertEqual(access_type.stage_count, 4)
        self.assertEqual(access_type.route_count, 3)

    def test_100_stage_previous_stage_ids(self):
        self.assertEqual(
            self.stage_draft.previous_stage_ids,
            self.stage_rejected)
        self.assertEqual(
            self.stage_sent.previous_stage_ids,
            self.stage_draft)
        self.assertEqual(
            self.stage_confirmed.previous_stage_ids,
            self.stage_sent)
        self.assertEqual(
            self.stage_rejected.previous_stage_ids,
            self.stage_sent)

    def test_110_stage_route_display_name_noname(self):
        self.route_draft_to_sent.name = False
        self.non_ascii_route_draft_to_sent.name = False

        self.assertEqual(
            self.route_draft_to_sent.display_name,
            "Draft -> Sent")

        self.assertEqual(
            self.non_ascii_route_draft_to_sent.display_name,
            u"Чорновик -> Відправлено")

    def test_115_stage_route_display_name_name(self):
        self.assertEqual(
            self.route_draft_to_sent.display_name,
            "Draft -> Sent [Send]")

    def test_117_stage_route_display_name_name_only(self):
        self.assertEqual(
            self.route_draft_to_sent.with_context(name_only=True).display_name,
            "Send")

    def test_117_stage_route_display_name_name_only_no_name(self):
        self.route_draft_to_sent.name = False
        self.assertEqual(
            self.route_draft_to_sent.with_context(name_only=True).display_name,
            "Draft -> Sent")

    def test_120_route_ensure_route__draft_sent(self):
        Route = self.env['request.stage.route']
        route = Route.ensure_route(
            self.request_1, self.stage_sent.id)
        self.assertTrue(route)
        self.assertEqual(len(route), 1)

    def test_125_route_ensure_route__draft_confirmed(self):
        Route = self.env['request.stage.route']

        with self.assertRaises(exceptions.ValidationError):
            Route.ensure_route(self.request_1, self.stage_confirmed.id)

    def test_130_request_create_simple(self):
        Request = self.env['request.request']

        request = Request.create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Request Text',
        })

        self.assertTrue(request.name.startswith('Req-'))
        self.assertEqual(request.stage_id, self.stage_draft)

    def test_135_request_create_and_assign(self):
        Request = self.env['request.request']

        request = Request.create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Request Text',
            'user_id': self.request_manager.id,
        })

        self.assertEqual(request.user_id, self.request_manager)
        self.assertTrue(request.date_assigned)

    def test_140_request_write_stage_sent(self):
        self.assertEqual(self.request_1.stage_id, self.stage_draft)

        self.request_1.write({'stage_id': self.stage_sent.id})

        self.assertEqual(self.request_1.stage_id, self.stage_sent)

    def test_145_request_write_stage_confirmed(self):
        self.assertEqual(self.request_1.stage_id, self.stage_draft)

        with self.assertRaises(exceptions.ValidationError):
            self.request_1.write({'stage_id': self.stage_confirmed.id})

    def test_150_request_type_sequence(self):
        Request = self.env['request.request']

        request = Request.create({
            'type_id': self.sequence_type.id,
            'category_id': self.resource_category.id,
            'request_text': 'Request Text',
        })

        self.assertTrue(request.name.startswith('RSR-'))
        self.assertEqual(request.stage_id, self.stage_new)

    def test_155_request__type_changed(self):
        Request = self.env['request.request']

        # Create new (empty) request
        request = Request.new({})
        self.assertFalse(request.stage_id)
        self.assertFalse(request.type_id)

        # Run onchange type_id:
        request.onchange_type_id()
        self.assertFalse(request.stage_id)
        self.assertFalse(request.type_id)

        request.type_id = self.simple_type
        self.assertFalse(request.stage_id)
        self.assertEqual(request.type_id, self.simple_type)

        request.onchange_type_id()
        self.assertEqual(request.stage_id, self.stage_draft)
        self.assertEqual(request.type_id, self.simple_type)

    def test_157_request__category_changed_restricts_type(self):
        # pylint: disable=too-many-statements
        deactivate_records_for_model(self.env, 'request.classifier')

        category_tech = self.env.ref(
            'generic_request.request_category_demo_technical_configuration')
        category_resource = self.env.ref(
            'generic_request.request_category_demo_resource')
        default_service = self.env.ref(
            'generic_service.generic_service_default')

        # Create New Request
        with Form(self.env['request.request']) as request_form:
            self.assertFalse(request_form.stage_id)
            self.assertFalse(request_form.type_id)
            self.assertFalse(request_form.stage_id)
            self.assertFalse(request_form.type_id)
            self.assertFalse(request_form.category_id)

            # Remove Default Service from category
            self.assertIn(default_service, category_tech.service_ids)

            # Remove link category with service
            self.Classifier.get_classifiers(
                service=default_service,
                category=category_tech).write({'active': False})
            self.env['request.classifier'].flush_model()
            self.assertNotIn(default_service, category_tech.service_ids)

            request_form.category_id = category_tech
            self.assertTrue(request_form.category_id)
            expected_classifier_type_ids = self.Classifier.search(
                [('category_id', '=', category_tech.id),
                 ('service_id', '=', False)]).mapped('type_id').ids
            self.assertListEqual(
                request_form.type_id_domain,
                ['&', ('start_stage_id', '!=', False),
                 ('id', 'in', expected_classifier_type_ids),
                 ])
            self.assertIn(self.access_type, category_tech.request_type_ids)
            self.assertEqual(request_form.category_id, category_tech)

            # Choose request type 'Grant Access'
            request_form.type_id = self.access_type
            self.assertEqual(request_form.type_id, self.access_type)
            self.assertEqual(request_form.stage_id,
                             self.access_type.start_stage_id)

            self.assertEqual(request_form.type_id, self.access_type)

            # Remove Default Service from category
            self.assertIn(default_service, category_resource.service_ids)

            # Remove link category with service
            self.Classifier.get_classifiers(
                service=default_service,
                category=category_resource).write({'active': False})
            self.env['request.classifier'].flush_model()
            self.assertNotIn(default_service, category_resource.service_ids)

            # Choose category Demo / Resource
            request_form.category_id = category_resource
            self.assertEqual(request_form.category_id, category_resource)
            self.assertNotIn(self.access_type,
                             category_resource.request_type_ids)

            self.assertFalse(request_form.type_id)
            self.assertFalse(request_form.stage_id)

            self.assertEqual(request_form.category_id, category_resource)
            expected_classifier_type_ids = self.Classifier.search(
                [('category_id', '=', category_resource.id),
                 ('service_id', '=', False)]).mapped('type_id').ids
            self.assertListEqual(
                request_form.type_id_domain,
                ['&', ('start_stage_id', '!=', False),
                 ('id', 'in', expected_classifier_type_ids),
                 ])
            # Choose type 'Printer Request'
            request_form.type_id = self.sequence_type
            self.assertEqual(request_form.type_id, self.sequence_type)
            self.assertEqual(request_form.stage_id,
                             self.sequence_type.start_stage_id)
            self.assertIn(self.sequence_type,
                          category_resource.request_type_ids)

            self.assertEqual(request_form.type_id, self.sequence_type)
            request_form.save()

    def test_160_request_category_display_name(self):
        self.assertEqual(
            self.tec_configuration_category.display_name,
            u"Demo / Technical / Configuration")

    def test_170_request_type_category_change(self):
        request = self.env['request.request'].create({
            'type_id': self.simple_type.id,
            'category_id': self.resource_category.id,
            'request_text': 'test',
        })
        self.env['request.classifier'].create({
            'type_id': self.simple_type.id,
            'category_id': self.tec_configuration_category.id,
        })

        with self.assertRaises(exceptions.ValidationError):
            request.write({'type_id': self.sequence_type.id})

        # Change category
        request.write({'category_id': self.tec_configuration_category.id})
        last_event = request.request_event_ids.sorted()[0]
        self.assertEqual(last_event.event_code, 'category-changed')
        self.assertEqual(last_event.old_category_id, self.resource_category)
        self.assertEqual(
            last_event.new_category_id, self.tec_configuration_category)

    def test_180_request_close_via_wizard(self):
        request = self.env.ref(
            'generic_request.request_request_type_sequence_demo_1')
        request.stage_id = self.env.ref(
            'generic_request.request_stage_type_sequence_sent')

        close_stage = self.env.ref(
            'generic_request.request_stage_type_sequence_closed')
        close_route = self.env.ref(
            'generic_request.request_stage_route_type_sequence_sent_to_closed')

        request.response_text = 'test response 1'

        act = request.action_close_request()

        request_closing = self.env[act['res_model']].with_context(
            **act['context'],
        ).create({
            'close_route_id': close_route.id,
        })
        request_closing.onchange_request_id()
        self.assertEqual(request_closing.response_text, request.response_text)
        self.assertEqual(request_closing.response_text,
                         '<p>test response 1</p>')

        request_closing.response_text = 'test response 42'
        request_closing.action_close_request()

        self.assertEqual(request.stage_id, close_stage)
        self.assertEqual(request.response_text, '<p>test response 42</p>')

    def test_request_html2text(self):
        self.assertEqual(html2text(False), "")
        self.assertEqual(html2text(None), "")
        self.assertEqual(
            html2text("<h1>Test</h1>").strip(), "# Test")

    def test_190_type_default_stages(self):
        type_default_stages = self.env['request.type'].with_context(
            create_default_stages=True).create({
                'name': "test-default-stages",
                'code': "test-default-stages",
            })
        self.assertEqual(type_default_stages.route_count, 1)
        self.assertEqual(
            type_default_stages.route_ids.stage_from_id.name, 'New')
        self.assertEqual(
            type_default_stages.route_ids.stage_to_id.name, 'Closed')

    def test_200_type_no_default_stages(self):
        type_no_default_stages = self.env['request.type'].create({
            'name': "test-no-default-stages",
            'code': "test-no-default-stages",
        })
        self.assertEqual(type_no_default_stages.route_count, 0)
        self.assertEqual(len(type_no_default_stages.stage_ids), 0)

        with self.assertRaises(exceptions.ValidationError):
            self.env['request.request'].create({
                'type_id': type_no_default_stages.id,
                'request_text': 'test',
            })

    def test_220_delete_stage_with_routes(self):
        with self.assertRaises(exceptions.ValidationError):
            self.stage_confirmed.unlink()

    def test_230_delete_stage_without_routes(self):
        stage = self.env['request.stage'].create({
            'name': 'Test',
            'code': 'test',
            'request_type_id': self.simple_type.id,
        })
        stage.unlink()  # no errors raised

    def test_240_request_events(self):
        with freeze_time('2018-07-09'):
            request = self.env['request.request'].create({
                'type_id': self.simple_type.id,
                'request_text': 'Test',
            })
            self.assertEqual(request.request_event_count, 1)
            self.assertEqual(
                request.request_event_ids.event_type_id.code, 'record-created')

        with freeze_time('2018-07-25'):
            # Change request text
            request.request_text = 'Test 42'

            # Refresh cache. This is required to read request_event_ids in
            # correct order
            request.invalidate_recordset()

            # Check that new event generated
            self.assertEqual(request.request_event_count, 2)
            self.assertEqual(
                request.request_event_ids[0].event_type_id.code, 'changed')
            self.assertEqual(
                request.request_event_ids[0].old_text, '<p>Test</p>')
            self.assertEqual(
                request.request_event_ids[0].new_text, '<p>Test 42</p>')

            # Test autovacuum of events (by default 90 days old)
            # No events removed, date not changed
            cron_job = self.env.ref(
                'generic_system_event.ir_cron_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 2)

        with freeze_time('2018-08-09'):
            # Test autovacuum of events (by default 90 days old)
            # No events removed, events not older that 90 days
            cron_job = self.env.ref(
                'generic_system_event.ir_cron_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 2)

        with freeze_time('2018-10-19'):
            # Test autovacuum of events (by default 90 days old)
            # One events removed, created event is older that 90 days
            cron_job = self.env.ref(
                'generic_system_event.ir_cron_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 1)
            self.assertEqual(
                request.request_event_ids.event_type_id.code, 'changed')
            self.assertEqual(
                request.request_event_ids.old_text, '<p>Test</p>')
            self.assertEqual(
                request.request_event_ids.new_text, '<p>Test 42</p>')

        self.env.ref(
            'generic_request.system_event_source__request_request'
        ).vacuum_enable = False

        with freeze_time('2018-10-27'):
            # Test autovacuum of events (by default 90 days old)
            # All events removed, all events older that 90 days
            cron_job = self.env.ref(
                'generic_system_event.ir_cron_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 1)

        with freeze_time('2018-12-27'):
            # Test autovacuum of events (by default 90 days old)
            # All events removed, all events older that 90 days
            cron_job = self.env.ref(
                'generic_system_event.ir_cron_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 1)

        self.env.ref(
            'generic_request.system_event_source__request_request'
        ).vacuum_enable = True

        with freeze_time('2018-12-27'):
            # Test autovacuum of events (by default 90 days old)
            # All events removed, all events older that 90 days
            cron_job = self.env.ref(
                'generic_system_event.ir_cron_vacuum_events')
            cron_job.method_direct_trigger()
            self.assertEqual(request.request_event_count, 0)

    def test_250_request_create_simple_without_channel(self):
        Request = self.env['request.request']
        channel_other = self.env.ref('generic_request.request_channel_other')

        request = Request.create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Request Text',
        })

        self.assertEqual(request.channel_id, channel_other)

    def test_251_request_channel_other_archived(self):
        Request = self.env['request.request']
        channel_other = self.env.ref('generic_request.request_channel_other')

        # Archive channel 'Other'
        channel_other.sudo().active = False
        channel_other.invalidate_recordset()

        # Check that archived channel is not assigned to the request
        request = Request.create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Request Text',
        })

        self.assertFalse(request.channel_id)

    def test_252_request_channel_other_deleted(self):
        Request = self.env['request.request']

        # Delete channel 'Other'
        self.env.ref('generic_request.request_channel_other').sudo().unlink()

        # Check that deleted channel is not assigned to the request
        request = Request.create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Request Text',
        })

        self.assertFalse(request.channel_id)

    def test_260_request_create_simple_with_channel_call(self):
        Request = self.env['request.request']
        channel_call = self.env.ref('generic_request.request_channel_call')

        request = Request.create({
            'type_id': self.simple_type.id,
            'category_id': self.general_category.id,
            'request_text': 'Request Text',
            'channel_id': channel_call.id,
        })

        self.assertEqual(request.channel_id, channel_call)

    def test_request_priority_changed_event_created(self):
        request = self.env['request.request'].create({
            'type_id': self.simple_type.id,
            'request_text': 'Test priority event',
        })
        self.assertEqual(request.request_event_count, 1)
        self.assertEqual(
            request.request_event_ids.event_type_id.code, 'record-created')

        # change priority
        request.priority = '4'

        # ensure event priority-changed created
        self.assertEqual(request.request_event_count, 2)
        self.assertSetEqual(
            set(request.request_event_ids.mapped('event_type_id.code')),
            {'record-created', 'priority-changed'})

    def test_unlink_just_created(self):
        request = self.env['request.request'].with_user(
            self.request_manager
        ).create({
            'type_id': self.simple_type.id,
            'request_text': 'test',
        })
        with self.assertRaises(exceptions.AccessError):
            request.unlink()

        # Managers with group *can delete requests* are allowed to delete
        # requests
        self.request_manager.groups_id |= self.env.ref(
            'generic_request.group_request_manager_can_delete_request')
        request.unlink()

    def test_unlink_processed(self):
        request = self.env['request.request'].with_user(
            self.request_manager
        ).create({
            'type_id': self.simple_type.id,
            'request_text': 'test',
        })
        request.request_text = 'test 42'
        request.user_id = self.request_manager

        with self.assertRaises(exceptions.AccessError):
            request.unlink()

        # Managers with group *can delete requests* are allowed to delete
        # requests
        self.request_manager.groups_id |= self.env.ref(
            'generic_request.group_request_manager_can_delete_request')
        request.unlink()

    def test_request_can_change_category(self):
        self.assertEqual(self.request_1.stage_id, self.stage_draft)
        self.assertTrue(self.request_1.can_change_category)

        # move request to sent stage
        self.request_1.stage_id = self.stage_sent

        # Check that changing category not allowed
        self.assertEqual(self.request_1.stage_id, self.stage_sent)
        self.assertFalse(self.request_1.can_change_category)

    def test_request_can_change_deadline(self):
        self.assertEqual(self.request_1.stage_id, self.stage_draft)
        self.assertTrue(self.request_1.can_change_deadline)

        # move request to sent stage
        self.request_1.stage_id = self.stage_sent

        # Check that changing deadline is allowed
        self.assertEqual(self.request_1.stage_id, self.stage_sent)
        self.assertTrue(self.request_1.can_change_deadline)

        # move request to confirmed stage
        self.request_1.stage_id = self.stage_confirmed

        # Check that changing deadline not allowed
        self.assertEqual(self.request_1.stage_id, self.stage_confirmed)
        self.assertFalse(self.request_1.can_change_deadline)

    def test_request_create_new_stage(self):
        stage = self.env['request.stage'].create({
            'request_type_id': self.simple_type.id,
            'name': 'Test',
            'code': 'test',
        })
        # Ensure that new stage is last stage
        self.assertEqual(stage, self.simple_type.stage_ids.sorted()[-1])

    def test_request_create_new_stage_with_sequence(self):
        stage = self.env['request.stage'].create({
            'request_type_id': self.simple_type.id,
            'name': 'Test',
            'code': 'test',
            'sequence': 0,
        })
        # Ensure that new stage is first stage
        self.assertEqual(stage, self.simple_type.stage_ids.sorted()[0])

    def test_request_create_first_stage(self):
        rtype = self.env['request.type'].with_context(
            create_default_stages=False,
        ).create({
            'name': 'Test Request Stages',
            'code': 'rest-request-stages',
        })

        self.assertFalse(rtype.stage_ids)

        # Create new stage
        stage = self.env['request.stage'].create({
            'request_type_id': rtype.id,
            'name': 'Test',
            'code': 'Test',
        })
        self.assertEqual(stage.sequence, 5)

    def test_request_suggested_recipients(self):
        author = self.env.ref('base.res_partner_address_7')
        partner = self.env.ref('base.res_partner_4')

        request = self.env.ref(
            'generic_request.request_request_type_simple_demo_3')

        # Check that author is auto subscribed, but partner is not subscribed
        self.assertIn(author, request.message_partner_ids)
        self.assertNotIn(partner, request.message_partner_ids)

        # By default suggestion for partner disabled, thus no partner
        # have to be suggested
        result = request._message_get_suggested_recipients()[request.id]
        partner_ids = [r[0] for r in result if r[0]]
        self.assertFalse(partner_ids)

        # But suggestion of email_cc is enabled
        partner_emails = [r[1] for r in result]
        self.assertIn('lquixley3@ning.com', partner_emails)
        self.assertIn('jhaddeston5@cafepress.com', partner_emails)

        # Enable suggestion for partner
        self.env.user.company_id.request_mail_suggest_partner = True

        result = request._message_get_suggested_recipients()[request.id]
        partner_ids = [r[0] for r in result if r[0]]
        self.assertEqual(len(partner_ids), 1)

        partner_emails = [r[1] for r in result]
        self.assertEqual(len(partner_emails), 3)

        # Ensure that partner is in suggested recipients
        self.assertNotIn(author.id, partner_ids)
        self.assertIn(partner.id, partner_ids)

        request.message_subscribe(partner_ids=partner.ids)

        # Ensure that after we subscribe partner it disappears from suggested
        # list
        result = request._message_get_suggested_recipients()[request.id]
        partner_ids = [r[0] for r in result if r[0]]
        self.assertFalse(partner_ids)

    def test_request_creation_template(self):
        request = self.creation_template.do_create_request({})
        self.assertEqual(
            request.category_id, self.creation_template.request_category_id)
        self.assertEqual(
            request.type_id, self.creation_template.request_type_id)
        self.assertEqual(
            request.request_text, self.creation_template.request_text)

    def test_request_kind_menuitem_toggle(self):
        self.assertFalse(self.request_kind.menuitem_toggle)
        self.assertFalse(self.request_kind.menuitem_name)
        self.assertFalse(self.request_kind.menuaction_name)

        # toggle (enable) menuitem button
        self.request_kind.menuitem_toggle = True

        self.assertTrue(self.request_kind.menuitem_id)
        self.assertTrue(self.request_kind.menuaction_id)
        self.assertEqual(
            self.request_kind.menuitem_name, self.request_kind.name
        )
        self.assertEqual(
            self.request_kind.menuaction_name, self.request_kind.name
        )

    def test_default_request_text(self):
        request = self.env['request.request'].new({
            'type_id': self.access_type.id,
            'category_id': self.tec_configuration_category.id,
            'user_id': self.request_manager.id,
        })
        self.assertFalse(request.request_text)

        request.onchange_type_id()

        self.assertEqual(request.request_text,
                         request.type_id.default_request_text)

    def test_default_response_text(self):
        request = self.request_2

        close_route = self.env.ref(
            'generic_request.request_stage_route_type_access_sent_to_rejected')
        close_stage = self.env.ref(
            'generic_request.request_stage_route_type_access_sent_to_rejected')

        request.stage_id = close_stage.id

        request_closing = self.env['request.wizard.close'].create({
            'request_id': request.id,
            'close_route_id': close_route.id,
        })
        self.assertFalse(request_closing.response_text)

        request_closing.onchange_close_route_id()

        self.assertEqual(request_closing.response_text,
                         close_route.default_response_text)

        request_closing.action_close_request()

        self.assertTrue(request.closed)

        self.assertEqual(request.response_text,
                         close_route.default_response_text)

        # toggle (disable) menuitem button
        self.request_kind.menuitem_toggle = False

        action = self.request_kind.menuaction_id

        self.assertFalse(self.request_kind.menuitem_id)
        self.assertFalse(self.request_kind.menuaction_id)

        self.assertFalse(action.exists())

    def test_complex_priority(self):
        test_request = self.env.ref(
            'generic_request.demo_request_with_complex_priority')

        # test complex priority
        self.assertEqual(test_request.priority, '2')

        # change impact and urgency
        test_request.impact = '0'
        test_request.urgency = '1'

        # test complex priority calculation
        self.assertEqual(test_request.priority, '1')

        event = self.env['request.event'].search(
            [('request_id', '=', test_request.id)])
        self.assertEqual(event[0].event_code, 'urgency-changed')
        self.assertEqual(event[1].event_code, 'priority-changed')
        self.assertEqual(event[2].event_code, 'impact-changed')
        self.assertEqual(event[3].event_code, 'priority-changed')

    def test_deadline_state_1(self):
        self.request_1.deadline_date = '2020-03-17'

        with freeze_time('2020-03-16'):
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'ok')

        with freeze_time('2020-03-17'):
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'today')

        with freeze_time('2020-03-18'):
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'overdue')

    def test_deadline_state_2(self):
        self.request_1.deadline_date = '2020-03-17'

        with freeze_time('2020-03-16'):
            self.request_1.stage_id = self.stage_sent
            self.request_1.stage_id = self.stage_confirmed
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'ok')

        with freeze_time('2020-03-18'):
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'ok')

    def test_deadline_state_3(self):
        self.request_1.deadline_date = '2020-03-17'

        with freeze_time('2020-03-17'):
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'today')

            self.request_1.stage_id = self.stage_sent
            self.request_1.stage_id = self.stage_confirmed
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'ok')

        with freeze_time('2020-03-18'):
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'ok')

    def test_deadline_state_4(self):
        self.request_1.deadline_date = '2020-03-17'

        with freeze_time('2020-03-18'):
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'overdue')

            self.request_1.stage_id = self.stage_sent
            self.request_1.stage_id = self.stage_confirmed
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'overdue')

        with freeze_time('2020-03-19'):
            self.request_1.invalidate_recordset()
            self.assertEqual(self.request_1.deadline_state, 'overdue')

    @mute_logger('odoo.sql_db')
    def test_20_request_type_name_uniq(self):
        Model = self.env['request.type']

        # Test name uniq constraint
        data1 = dict(code='TEST-CODE-1', name='Test Type Name 42')
        data2 = dict(code='TEST-CODE-2', name='Test Type Name 42')

        Model.create(dict(data1))
        with self.assertRaises(IntegrityError):
            Model.create(dict(data2))

    @mute_logger('odoo.sql_db')
    def test_30_request_type_code_uniq(self):
        Model = self.env['request.type']

        # Test code uniq constraints
        data1 = dict(code='TEST-CODE-4', name='Test Type Name 44')
        data2 = dict(code='TEST-CODE-4', name='Test Type Name 45')

        Model.create(dict(data1))
        with self.assertRaises(IntegrityError):
            Model.create(dict(data2))

    @mute_logger('odoo.sql_db')
    def test_40_request_type_code_ascii(self):
        Model = self.env['request.type']

        # Test code uniq constraints
        data1 = dict(code='TEST-CODE-4', name='Test Type Name 44')
        data2 = dict(code='Тестовий-код-5', name='Test Type Name 45')

        Model.create(dict(data1))
        with self.assertRaises(IntegrityError):
            Model.create(dict(data2))

    def test_request_author_changed_event_created(self):
        request = self.env.ref(
            'generic_request.request_request_type_simple_demo_1'
        )
        self.assertNotIn(
            'author-changed',
            self._get_events(request).mapped('event_code'))

        # Try to change the author of request
        current_author_id = request.author_id.ids[0]
        author_ids = list(filter(lambda x: x != current_author_id, (
            self.env['res.partner'].search([('is_company', '=', False)])).ids))
        request.author_id = author_ids[0]

        # Ensure that 'author-changed' event was generated
        self.assertIn(
            'author-changed',
            self._get_events(request).mapped('event_code'))

    def test_request_partner_changed_event_created(self):
        request = self.env.ref(
            'generic_request.request_request_type_simple_demo_1'
        )
        self.assertNotIn(
            'partner-changed',
            self._get_events(request).mapped('event_code'))

        # Try to change the author of request
        current_partner_id = request.partner_id.ids[0]
        partner_ids = list(filter(lambda x: x != current_partner_id, (
            self.env['res.partner'].search([])).ids))
        request.partner_id = partner_ids[0]

        # Ensure that 'author-changed' event was generated
        self.assertIn(
            'partner-changed',
            self._get_events(request).mapped('event_code'))

    def test_access_request_to_change_active(self):
        request = self.env['request.request'].with_user(
            self.request_manager
        ).create({
            'type_id': self.simple_type.id,
            'request_text': 'test',
        })

        group_allow_archive = self.env.ref(
            'generic_request.group_request_manager_can_archive_request')

        # Check user no have group allow archive
        self.assertNotIn(
            group_allow_archive.id, self.request_manager.groups_id.ids)
        self.assertEqual(request.active, True)

        # User wihout Request group allow archive can't change active
        with self.assertRaises(exceptions.AccessError):
            request.with_user(self.request_manager).write({
                'active': False})

        self.request_manager.groups_id |= group_allow_archive
        self.assertIn(
            group_allow_archive.id, self.request_manager.groups_id.ids)
        request.with_user(self.request_manager).write({
            'active': False})

        # SUPERUSER can archive request witout group
        user_admin = self.env.ref('base.user_root')
        self.assertNotIn(
            group_allow_archive.id, user_admin.groups_id.ids)
        self.request_1.with_user(user_admin).write({
            'active': True})

    def test_request_action_preferred_list(self):
        self.env.user.company_id.request_preferred_list_view_mode = 'list'
        request_act = self.env.ref(
            'generic_request.action_request_window',
            raise_if_not_found=False)
        # Views is [(view_id, view_mode),(view_id, view_mode)]
        self.assertEqual(
            request_act.read(['views'])[0]['views'][0][1], 'tree')
        self.assertEqual(
            request_act.read(['views'])[0]['views'][1][1], 'kanban')

    def test_request_action_preferred_kanban(self):
        self.env.user.company_id.request_preferred_list_view_mode = 'kanban'
        request_act = self.env.ref(
            'generic_request.action_request_window',
            raise_if_not_found=False)
        # Views is [(view_id, view_mode),(view_id, view_mode)]
        self.assertEqual(
            request_act.read(['views'])[0]['views'][0][1], 'kanban')
        self.assertEqual(
            request_act.read(['views'])[0]['views'][1][1], 'tree')

    def test_request_action_preferred_default(self):
        # Test configuration, when preferred view mode is set to 'default'
        self.env.user.company_id.request_preferred_list_view_mode = 'default'
        request_act = self.env.ref(
            'generic_request.action_request_window',
            raise_if_not_found=False)

        # Change view mode, and expect that 'views' will still be based on
        # 'view_mode'
        request_act.write({
            'view_mode': 'pivot,kanban,tree,graph,form,activity',
        })
        # Views is [(view_id, view_mode),(view_id, view_mode)]
        self.assertEqual(
            request_act.read(['views'])[0]['views'][0][1], 'pivot')
        self.assertEqual(
            request_act.read(['views'])[0]['views'][1][1], 'kanban')

    def test_request_event_live_time_uom_false(self):
        with freeze_time('2018-07-09'):
            request = self.env['request.request'].create({
                'type_id': self.simple_type.id,
                'request_text': 'Test autovacuum',
            })
            event_source = self.env.ref(
                'generic_request.system_event_source__request_request')
            event_source.vacuum_enable = True
            event_source.vacuum_time = 2
            event_source.vacuum_time_uom = False
            self.assertEqual(request.request_event_count, 1)

        with freeze_time('2018-07-12'):
            # Test autovacuum of events (set 2 day)
            # No events was removed, autovacuum skipped (uom = False)
            cron_job = self.env.ref(
                'generic_system_event.ir_cron_vacuum_events')

            with self.assertRaises(exceptions.UserError):
                cron_job.method_direct_trigger()

            self.assertEqual(request.request_event_count, 1)

    def test_wizard_base_partner_merge(self):
        # Check that request counter of demo_user matchs its request amount
        self.assertEqual(self.demo_user.request_count,
                         len(self.demo_user.request_ids))
        demo_user_request_count = self.demo_user.request_count

        # Create test partner to test a merge with it
        test_partner = self.env['res.partner'].create({
            'name': 'Test merge partner'
        })
        self.request_1.write({
            'author_id': test_partner.id
        })

        # Check that request counter of request_user matchs its request amount
        self.assertEqual(test_partner.request_count,
                         len(test_partner.request_ids))
        test_partner_request_count = test_partner.request_count
        self.assertEqual(test_partner_request_count, 1)

        # Create and action merge wizard
        wizard = self.env['base.partner.merge.automatic.wizard'].create({
            'dst_partner_id': self.demo_user.partner_id.id,
            'partner_ids': [(4, test_partner.id),
                            (4, self.demo_user.partner_id.id)]
        })
        wizard.action_merge()

        # Check that target user merged the requests of source contact
        self.assertEqual(self.demo_user.request_count,
                         demo_user_request_count + test_partner_request_count)
        self.assertEqual(self.demo_user.request_count,
                         len(self.demo_user.request_ids))

    def test_request_deadline_events(self):
        # Test deadlinee events when deadline set via date field.
        # pylint: disable=too-many-statements
        self.assertEqual(self.request_1.type_id.deadline_format, 'date')
        with freeze_time('2020-03-07'):
            self.request_1.deadline_date = '2020-03-10'
            cron_job = self.env.ref(
                'generic_request.ir_cron_request_check_deadlines')
            # TODO: During the migration, there will be a quantity error,
            # because the service-related event ('service-level-changed')
            # will be missing on the previously created requests.
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 2)

        # Check no deadline events created over 2 day to deadline
        with freeze_time('2020-03-08'):
            cron_job.method_direct_trigger()
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 2)

        # Check that event 'deadline-tomorrow' created 1 day before deadline
        with freeze_time('2020-03-09'):
            cron_job.method_direct_trigger()
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 3)
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertIn('deadline-tomorrow', events)

        # Check that event 'deadline-today' created in deadline date
        with freeze_time('2020-03-10'):
            cron_job.method_direct_trigger()
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 4)
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertIn('deadline-today', events)

        # Check that event 'deadline-overdue' created 1 day after deadline
        with freeze_time('2020-03-11'):
            cron_job.method_direct_trigger()
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 5)
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertIn('deadline-overdue', events)

            # Check that repeated cron action wouldn't generate same events
            cron_job.method_direct_trigger()
            events = self.request_1.request_event_ids.mapped('event_code')
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 5)
            self.assertEqual(events.count('deadline-overdue'), 1)

        # Check no more deadline events created 2 days after deadline
        with freeze_time('2020-03-12'):
            cron_job.method_direct_trigger()
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 5)

        # Check that event generated when deadline changed on future date
        # immediately
        with freeze_time('2020-03-13'):
            self.request_1.deadline_date = '2020-03-14'
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 7)
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 1)
            self.assertEqual(events.count('deadline-today'), 1)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 2)

        # Check that event is generated by cron when new deadline reached
        with freeze_time('2020-03-14'):
            cron_job.method_direct_trigger()
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 8)
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 1)
            self.assertEqual(events.count('deadline-today'), 2)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 2)

        # Check that overdue event generated when changing deadline
        # to past date
        with freeze_time('2020-03-14'):
            self.request_1.deadline_date = '2020-03-11'
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 10)
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 2)
            self.assertEqual(events.count('deadline-today'), 2)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 3)

        # Check that no new event generated by cron
        with freeze_time('2020-03-14'):
            cron_job.method_direct_trigger()
            events = self.request_1.request_event_ids.mapped('event_code')
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 10)
            self.assertEqual(events.count('deadline-overdue'), 2)
            self.assertEqual(events.count('deadline-today'), 2)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 3)

        # Test that 'deadline-today' event will be triggered immediately
        with freeze_time('2020-03-14'):
            self.request_1.deadline_date = '2020-03-14'
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 12)
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 2)
            self.assertEqual(events.count('deadline-today'), 3)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 4)

        # Check that no new event generated by cron
        with freeze_time('2020-03-14'):
            cron_job.method_direct_trigger()
            event_count = self._get_event_count(
                self.request_1, exclude_codes=['service-level-changed'])
            self.assertEqual(event_count, 12)
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 2)
            self.assertEqual(events.count('deadline-today'), 3)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 4)

    def test_request_deadline_events_dt(self):
        # Test deadlinee events when deadline set via datetime field.
        # pylint: disable=too-many-statements
        self.request_1.type_id.deadline_format = 'datetime'
        self.assertEqual(self.request_1.type_id.deadline_format, 'datetime')
        with freeze_time('2020-03-07 00:00:00'):
            self.assertTrue(self.request_1.deadline_date)
            self.assertEventCount(
                self.request_1, 0, only_codes=['deadline-changed'])
            self.request_1.deadline_date_dt = '2020-03-10 07:00:00'
            cron_job = self.env.ref(
                'generic_request.ir_cron_request_check_deadlines')
            self.assertEventCount(
                self.request_1, 1, only_codes=['deadline-changed'])
            self.assertEventCount(
                self.request_1, 2,  exclude_codes=['service-level-changed'])

        # Check no deadline events created over 2 day to deadline
        with freeze_time('2020-03-08 00:00:00'):
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 2,  exclude_codes=['service-level-changed'])

        # Check that event 'deadline-tomorrow' created 1 day before deadline
        with freeze_time('2020-03-09 00:00:00'):
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 3,  exclude_codes=['service-level-changed'])
            self.assertEventCount(
                self.request_1, 1,  only_codes=['deadline-tomorrow'])

        # Check that event 'deadline-today' created in deadline date
        with freeze_time('2020-03-10 07:00:00'):
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 4,  exclude_codes=['service-level-changed'])
            self.assertEventCount(
                self.request_1, 1,  only_codes=['deadline-today'])

        # Check that event 'deadline-overdue' generated
        with freeze_time('2020-03-10 07:00:01'):
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 5,  exclude_codes=['service-level-changed'])
            self.assertEventCount(
                self.request_1, 1,  only_codes=['deadline-overdue'])

        # Check that event 'deadline-overdue' no more generated
        with freeze_time('2020-03-11 00:00:00'):
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 5,  exclude_codes=['service-level-changed'])
            self.assertEventCount(
                self.request_1, 1,  only_codes=['deadline-overdue'])

            # Check that repeated cron action wouldn't generate same events
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 5,  exclude_codes=['service-level-changed'])
            self.assertEventCount(
                self.request_1, 1,  only_codes=['deadline-overdue'])

        # Check no more deadline events created 2 days after deadline
        with freeze_time('2020-03-12 00:00:00'):
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 5,  exclude_codes=['service-level-changed'])

        # Check that event generated when deadline changed on future date
        # immediately
        with freeze_time('2020-03-13 00:00:00'):
            self.request_1.deadline_date_dt = '2020-03-14 23:59:59'
            self.assertEventCount(
                self.request_1, 7,  exclude_codes=['service-level-changed'])
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 1)
            self.assertEqual(events.count('deadline-today'), 1)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 2)

        # Check that event is generated by cron when new deadline reached
        with freeze_time('2020-03-14 00:00:00'):
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 8,  exclude_codes=['service-level-changed'])
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 1)
            self.assertEqual(events.count('deadline-today'), 2)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 2)

        # Check that overdue event generated when changing deadline
        # to past date
        with freeze_time('2020-03-14 00:00:00'):
            self.request_1.deadline_date_dt = '2020-03-11 23:59:59'
            self.assertEventCount(
                self.request_1, 10,  exclude_codes=['service-level-changed'])
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 2)
            self.assertEqual(events.count('deadline-today'), 2)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 3)

        # Check that no new event generated by cron
        with freeze_time('2020-03-14 00:00:00'):
            cron_job.method_direct_trigger()
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEventCount(
                self.request_1, 10,  exclude_codes=['service-level-changed'])
            self.assertEqual(events.count('deadline-overdue'), 2)
            self.assertEqual(events.count('deadline-today'), 2)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 3)

        # Test that 'deadline-today' event will be triggered immediately
        with freeze_time('2020-03-14 00:00:00'):
            self.request_1.deadline_date_dt = '2020-03-14 23:59:59'
            self.assertEventCount(
                self.request_1, 12,  exclude_codes=['service-level-changed'])
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 2)
            self.assertEqual(events.count('deadline-today'), 3)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 4)

        # Check that no new event generated by cron
        with freeze_time('2020-03-14 00:00:00'):
            cron_job.method_direct_trigger()
            self.assertEventCount(
                self.request_1, 12,  exclude_codes=['service-level-changed'])
            events = self.request_1.request_event_ids.mapped('event_code')
            self.assertEqual(events.count('deadline-overdue'), 2)
            self.assertEqual(events.count('deadline-today'), 3)
            self.assertEqual(events.count('deadline-tomorrow'), 2)
            self.assertEqual(events.count('deadline-changed'), 4)

    def test_request_delete_ensure_events(self):
        request = self.env.ref(
            'generic_request.request_request_type_simple_demo_long_text_1')
        user = self.request_user

        self.assertEqual(request.stage_id, self.stage_draft)

        # Make request sent
        request.with_user(user).write({'stage_id': self.stage_sent.id})
        self.assertEqual(request.stage_id, self.stage_sent)
        self.assertFalse(request.date_closed)
        self.assertFalse(request.closed_by_id)

        # Delete request and check that events were removed
        events = self._get_events(request)
        base_events = events.mapped('event_id')

        self.assertGreaterEqual(len(events), 1)
        self.assertEqual(len(events), len(base_events))

        request.unlink()

        self.assertFalse(events.exists())
        self.assertFalse(base_events.exists())

    def test_copy_request_type(self):
        new_type1 = self.simple_type.copy()
        self.assertEqual(new_type1.name, "Simple Request (Copy)")
        self.assertEqual(new_type1.code, "simple-copy")

        new_type2 = self.simple_type.copy()
        self.assertEqual(new_type2.name, "Simple Request (Copy) [1]")
        self.assertEqual(new_type2.code, "simple-copy-1")

        new_type3 = self.simple_type.copy()
        self.assertEqual(new_type3.name, "Simple Request (Copy) [2]")
        self.assertEqual(new_type3.code, "simple-copy-2")

        stage_codes = new_type3.stage_ids.mapped('code')
        self.assertIn('draft', stage_codes)
        self.assertIn('sent', stage_codes)
        self.assertIn('confirmed', stage_codes)
        self.assertIn('rejected', stage_codes)
        self.assertEqual(len(stage_codes), 4)

        stage_routes = [
            (r.stage_from_id.code, r.stage_to_id.code)
            for r in new_type3.route_ids
        ]
        self.assertIn(('draft', 'sent'), stage_routes)
        self.assertIn(('sent', 'confirmed'), stage_routes)
        self.assertIn(('sent', 'rejected'), stage_routes)
        self.assertIn(('rejected', 'draft'), stage_routes)
        self.assertEqual(len(stage_routes), 4)

    def test_request_deadline_states(self):
        Request = self.env['request.request']
        self.simple_type.write({
            'deadline_format': 'datetime',
        })
        self.env.user.tz = 'Europe/Kiev'
        self.assertEqual(self.simple_type.deadline_format, 'datetime')
        self.assertEqual(self.env.user.tz, 'Europe/Kiev')

        with Form(Request) as request_form:
            with freeze_time('2020-03-14 00:01:00', tz_offset=-2):
                request_form.category_id = self.general_category
                request_form.type_id = self.simple_type

                # Check deadline state today on the edge of the current day.
                # As db writes datetimes in UTC, convert it
                deadline = fields.datetime.strptime(
                    '2020-03-14 23:59:59', '%Y-%m-%d %H:%M:%S')
                utc_deadline = get_utc_datetime(
                    timezone='Europe/Kiev', dt=deadline)
                request_form.deadline_date_dt = utc_deadline
                self.assertEqual(request_form.deadline_state, 'today')

                deadline = fields.datetime.strptime(
                    '2020-03-14 00:02:00', '%Y-%m-%d %H:%M:%S')
                utc_deadline = get_utc_datetime(
                    timezone='Europe/Kiev', dt=deadline)
                request_form.deadline_date_dt = utc_deadline
                self.assertEqual(request_form.deadline_state, 'today')

                # Check deadline state overdue
                deadline = fields.datetime.strptime(
                    '2020-03-14 00:00:58', '%Y-%m-%d %H:%M:%S')
                utc_deadline = get_utc_datetime(
                    timezone='Europe/Kiev', dt=deadline)
                request_form.deadline_date_dt = utc_deadline
                self.assertEqual(request_form.deadline_state, 'overdue')

                # Check deadline state ok
                deadline = fields.datetime.strptime(
                    '2020-03-15 00:00:00', '%Y-%m-%d %H:%M:%S')
                utc_deadline = get_utc_datetime(
                    timezone='Europe/Kiev', dt=deadline)
                request_form.deadline_date_dt = utc_deadline
                self.assertEqual(request_form.deadline_state, 'ok')
                request_form.request_text = 'test deadline states'
                request_form.save()
