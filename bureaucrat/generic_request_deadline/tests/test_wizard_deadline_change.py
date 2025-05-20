from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from odoo.tests.common import TransactionCase
from odoo.addons.generic_mixin.tests.common import FindNew
from odoo import fields


class TestWizardDeadlineChange(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWizardDeadlineChange, cls).setUpClass()
        cls.event_deadline_changed = cls.env.ref(
            'generic_request.request_event_type_deadline_changed')
        cls.test_request = cls.env.ref(
            'generic_request.request_request_reopen_main_1')
        cls.test_request_type = cls.env.ref(
            'generic_request.request_type_reopen_main')
        cls.user_admin = cls.env.ref('base.user_root')
        cls.demo_user = cls.env.ref('base.user_demo')
        cls.group_request_manager = cls.env.ref(
            'generic_request.group_request_manager')
        cls.deadline_change_reason_technical = cls.env.ref(
            'generic_request_deadline.deadline_change_reason_technical')
        cls.deadline_change_reason_new_info = cls.env.ref(
            'generic_request_deadline.deadline_change_reason_additional_info')

    def flush_tracking(self):
        """ Force the creation of tracking values. """
        self.env.flush_all()
        self.cr.precommit.run()

    def test_request_wizard_deadline_change(self):
        # Check request has no event 'deadline-changed'
        today_dt = fields.Date.today().strftime('%Y-%m-%d 23:59:59')
        self.assertFalse(self.test_request.deadline_date)
        self.assertNotIn(
            'deadline-changed',
            self.test_request.request_event_ids.mapped('event_code'))

        # change deadline date
        self.test_request.deadline_date_dt = today_dt
        self.assertTrue(self.test_request.deadline_date)
        self.assertIn('deadline-changed',
                      self.test_request.request_event_ids.mapped('event_code'))

        # create wizard to change deadline
        change_deadline_comment = 'The technical possibilities do not ' \
                                  'allow complete ticket on time'
        wizard_change_deadline = self.env[
            'request.wizard.change.deadline'].new({
                'request_id': self.test_request.id,
                'deadline_date': fields.Date.today() + relativedelta(days=4),
                'deadline_change_reason_id':
                    self.deadline_change_reason_technical.id,
                'deadline_change_comment': change_deadline_comment})
        with FindNew(self.env, 'request.event') as nr:
            wizard_change_deadline.action_change_deadline()
        event = nr['request.event']

        # Check event created and has deadline change information
        self.assertEqual(event.event_code, 'deadline-changed')
        self.assertEqual(event.deadline_change_reason_id,
                         self.deadline_change_reason_technical)
        self.assertEqual(
            event.deadline_change_comment, change_deadline_comment)
        self.assertEqual(
            self.test_request.deadline_date,
            fields.Date.today() + relativedelta(days=4))

    def test_default_notification_strict_deadline(self):

        # Set initial values
        today_date = fields.Date.today()
        self.assertFalse(self.test_request.deadline_date)
        self.test_request_type.use_strict_deadline = True
        self.assertTrue(self.test_request_type.use_strict_deadline)
        self.assertTrue(self.test_request.strict_deadline)
        self.assertEqual(self.test_request.deadline_format, 'date')

        # Create wizard to change deadline
        change_deadline_comment = 'Test comment'
        change_reason = self.deadline_change_reason_technical
        wizard_change_deadline = self.env[
            'request.wizard.change.deadline'].new({
                'request_id': self.test_request.id,
                'deadline_date': today_date + relativedelta(days=4),
                'deadline_change_reason_id': change_reason.id,
                'deadline_change_comment': change_deadline_comment})

        # Set request deadline
        with FindNew(self.env, 'mail.message') as nr:
            wizard_change_deadline.action_change_deadline()
            self.assertTrue(self.test_request.deadline_date)
            self.flush_tracking()

        # Check message generated properly
        message = nr['mail.message']
        self.assertEqual(len(message), 1)
        expected_notification_body = Markup(
            "<p>Deadline changed!</p>"
            "<p>Reason: <strong>{reason_name}</strong></p>"
            "<p>Comments: <i>{comment}</i></p>").format(
            reason_name=self.deadline_change_reason_technical.name,
            comment=change_deadline_comment)  # nosec
        self.assertEqual(message.body, expected_notification_body)
        message_tracked_field = message.tracking_value_ids.field_id.name
        self.assertEqual(message_tracked_field, 'deadline_date')

        # Change deadline format
        self.test_request_type.deadline_format = 'datetime'
        self.assertEqual(self.test_request.deadline_format, 'datetime')

        # Create wizard to change deadline
        change_deadline_comment = 'Test comment datetime format'
        change_reason = self.deadline_change_reason_new_info
        wizard_change_deadline = self.env[
            'request.wizard.change.deadline'].new({
                'request_id': self.test_request.id,
                'deadline_dt': today_date + relativedelta(days=4, hours=3),
                'deadline_change_reason_id': change_reason.id,
                'deadline_change_comment': change_deadline_comment})

        # Set request deadline
        with FindNew(self.env, 'mail.message') as nr:
            wizard_change_deadline.action_change_deadline()
            self.assertTrue(self.test_request.deadline_date)
            self.flush_tracking()

        # Check message generated properly
        message = nr['mail.message']
        self.assertEqual(len(message), 1)
        expected_notification_body = Markup(
            "<p>Deadline changed!</p>"
            "<p>Reason: <strong>{reason_name}</strong></p>"
            "<p>Comments: <i>{comment}</i></p>").format(
            reason_name=self.deadline_change_reason_new_info.name,
            comment=change_deadline_comment)  # nosec
        self.assertEqual(message.body, expected_notification_body)
        message_tracked_field = message.tracking_value_ids.field_id.name
        self.assertEqual(message_tracked_field, 'deadline_date_dt')
