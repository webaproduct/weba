from odoo.addons.generic_request.tests.common import RequestCase, freeze_time


class TestDeadlineOverdue(RequestCase):
    @classmethod
    def setUpClass(cls):
        super(TestDeadlineOverdue, cls).setUpClass()
        cls.cron_check_deadline = cls.env.ref(
            'generic_request.ir_cron_request_check_deadlines')

    def test_request_deadline_dt_overdue(self):
        self.request_1.deadline_date = False
        self.request_1.type_id.deadline_format = 'datetime'
        self.assertEqual(self.request_1.type_id.deadline_format, 'datetime')
        self.assertFalse(self.request_1.deadline_date_dt)
        self.assertFalse(self.request_1.deadline_overdue)

        # Set deadline for request
        with freeze_time('2020-03-07 00:00:00'):
            self.request_1.deadline_date_dt = '2020-03-10 10:00:00'
            self.assertTrue(self.request_1.deadline_date_dt)
            self.assertFalse(self.request_1.deadline_overdue)

        # Check deadline overdue by 1 hour
        with freeze_time('2020-03-10 11:00:00'):
            # Run cron to check deadlines
            self.cron_check_deadline.method_direct_trigger()
            self.assertTrue(self.request_1.deadline_overdue)
            # Check deadline overdue by 1 hour
            self.assertEqual(self.request_1.deadline_overdue, 1.0)

        # Change stage to trigger deadline overdue recompute
        with freeze_time('2020-03-10 12:30:00'):
            self.assertEqual(self.request_1.stage_id.code, 'draft')
            self.request_1.stage_id = self.stage_sent
            self.assertTrue(self.request_1.deadline_overdue)

            # Check deadline overdue by 2.5 hour
            self.assertEqual(self.request_1.deadline_overdue, 2.5)

        # Check deadline recomputes when request close
        with freeze_time('2020-03-10 15:30:00'):
            self.assertEqual(self.request_1.deadline_overdue, 2.5)
            # Close request
            self.request_1.stage_id = self.stage_confirmed
            # Check deadline overdue by 5.5 hour
            self.assertEqual(self.request_1.deadline_overdue, 5.5)

        # Check that closed request doesnt recompute deadline overdue
        with freeze_time('2020-03-20 13:00:00'):
            self.assertEqual(self.request_1.deadline_overdue, 5.5)
            self.cron_check_deadline.method_direct_trigger()
            self.assertEqual(self.request_1.deadline_overdue, 5.5)

    def test_request_deadline_date_overdue(self):
        self.request_1.deadline_date = False
        self.request_1.type_id.deadline_format = 'date'
        self.assertEqual(self.request_1.type_id.deadline_format, 'date')
        self.assertFalse(self.request_1.deadline_date)
        self.assertFalse(self.request_1.deadline_overdue)

        # Set deadline for request
        with freeze_time('2020-03-07 00:00:00'):
            self.request_1.deadline_date = '2020-03-09'
            self.assertTrue(self.request_1.deadline_date)
            self.assertFalse(self.request_1.deadline_overdue)

        # Check deadline overdue by 2 days (48 hours)
        with freeze_time('2020-03-11 12:00:00'):
            # Run cron to check deadlines
            self.cron_check_deadline.method_direct_trigger()
            self.assertTrue(self.request_1.deadline_overdue)
            # Check deadline overdue by 2 days
            self.assertEqual(self.request_1.deadline_overdue, 48.0)

        # Change stage to trigger deadline overdue recompute
        with freeze_time('2020-03-12 22:30:00'):
            # Change stage to recompute deadline overdue
            self.assertEqual(self.request_1.stage_id.code, 'draft')
            self.request_1.stage_id = self.stage_sent
            self.assertTrue(self.request_1.deadline_overdue)

            # Check deadline overdue by 3 days (72 hours)
            self.assertEqual(self.request_1.deadline_overdue, 72.0)

        # Check deadline recomputes when request close
        with freeze_time('2020-03-13 15:30:00'):
            self.assertEqual(self.request_1.deadline_overdue, 72.0)
            # Close request
            self.request_1.stage_id = self.stage_confirmed
            # Check deadline overdue by 4 days (96 hours)
            self.assertEqual(self.request_1.deadline_overdue, 96.0)

        # Check that closed request doesnt recompute deadline overdue
        with freeze_time('2020-03-20 13:00:00'):
            self.assertEqual(self.request_1.deadline_overdue, 96.0)
            self.cron_check_deadline.method_direct_trigger()
            self.assertEqual(self.request_1.deadline_overdue, 96.0)

    def test_scheduler_deadline_update_datetime(self):
        """Test that scheduler correctly updates deadline_overdue for open
        requests with datetime format"""
        # Set up test request
        self.request_1.deadline_date = False
        self.request_1.type_id.deadline_format = 'datetime'
        self.assertEqual(self.request_1.type_id.deadline_format, 'datetime')
        self.assertFalse(self.request_1.deadline_date_dt)
        self.assertFalse(self.request_1.deadline_overdue)

        # Set deadline for request
        with freeze_time('2020-03-07 00:00:00'):
            self.request_1.deadline_date_dt = '2020-03-10 10:00:00'
            self.assertTrue(self.request_1.deadline_date_dt)
            self.assertFalse(self.request_1.deadline_overdue)

        # Check that scheduler updates deadline overdue by 1 hour
        with freeze_time('2020-03-10 11:00:00'):
            # Run scheduler to update deadline overdue
            self.env['request.request'].scheduler_update_deadline_overdue()
            self.assertTrue(self.request_1.deadline_overdue)
            # Check deadline overdue by 1 hour
            self.assertEqual(self.request_1.deadline_overdue, 1.0)

        # Check scheduler updates deadline overdue by 5.5 hours
        with freeze_time('2020-03-10 15:30:00'):
            # Run scheduler
            self.env['request.request'].scheduler_update_deadline_overdue()
            # Check deadline overdue by 5.5 hour
            self.assertEqual(self.request_1.deadline_overdue, 5.5)

    def test_scheduler_deadline_update_date(self):
        """Test that scheduler correctly updates deadline_overdue for open
        requests with date format"""
        # Set up test request
        self.request_1.deadline_date = False
        self.request_1.type_id.deadline_format = 'date'
        self.assertEqual(self.request_1.type_id.deadline_format, 'date')
        self.assertFalse(self.request_1.deadline_date)
        self.assertFalse(self.request_1.deadline_overdue)

        # Set deadline for request
        with freeze_time('2020-03-07 00:00:00'):
            self.request_1.deadline_date = '2020-03-09'
            self.assertTrue(self.request_1.deadline_date)
            self.assertFalse(self.request_1.deadline_overdue)

        # Check that scheduler updates deadline overdue by 2 days (48 hours)
        with freeze_time('2020-03-11 12:00:00'):
            # Run scheduler to update deadline overdue
            self.env['request.request'].scheduler_update_deadline_overdue()
            self.assertTrue(self.request_1.deadline_overdue)
            # Check deadline overdue by 2 days
            self.assertEqual(self.request_1.deadline_overdue, 48.0)

    def test_scheduler_doesnt_update_closed_requests(self):
        """Test that scheduler doesn't update deadline_overdue for closed
        requests"""
        # Set up test request
        self.request_1.deadline_date = False
        self.request_1.type_id.deadline_format = 'datetime'
        self.assertEqual(self.request_1.type_id.deadline_format, 'datetime')

        # Set deadline for request and create initial overdue value
        with freeze_time('2020-03-07 00:00:00'):
            self.request_1.deadline_date_dt = '2020-03-10 10:00:00'
            self.assertTrue(self.request_1.deadline_date_dt)
            self.assertFalse(self.request_1.deadline_overdue)

        # Create overdue value and close request
        with freeze_time('2020-03-10 15:30:00'):
            # Run scheduler to update deadline overdue
            self.env['request.request'].scheduler_update_deadline_overdue()
            self.assertEqual(self.request_1.deadline_overdue, 5.5)

            # First move to sent stage
            self.request_1.stage_id = self.stage_sent
            # Then move to confirmed stage
            self.request_1.stage_id = self.stage_confirmed
            self.assertTrue(self.request_1.closed)

        # Check that scheduler doesn't update deadline overdue for closed
        # request
        with freeze_time('2020-03-20 15:30:00'):
            # Memorize current overdue value
            current_overdue = self.request_1.deadline_overdue
            self.assertEqual(current_overdue, 5.5)
            # Run scheduler
            self.env['request.request'].scheduler_update_deadline_overdue()
            # Check that overdue value hasn't changed
            self.assertEqual(self.request_1.deadline_overdue, current_overdue)
