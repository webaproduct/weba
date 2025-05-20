import logging
import re
from dateutil.relativedelta import relativedelta
from odoo.addons.mail.models.mail_mail import MailMail
from odoo import fields
from odoo.tests import HttpCase
from odoo.tools.misc import mute_logger
from odoo.addons.generic_mixin.tests.common import (
    AccessRulesFixMixinMT,
    deactivate_records_for_model,
    FindNew,
)
# from .common import disable_mail_auto_delete

_logger = logging.getLogger(__name__)


class TestRequestMailNotificationLinks(AccessRulesFixMixinMT, HttpCase):

    def setUp(self):
        super(TestRequestMailNotificationLinks, self).setUp()

        self.request_demo_user = self.env.ref(
            'generic_request.user_demo_request')
        self.user_root = self.env.ref('base.user_root')

        # Subscribe demo user to printer request
        self.env.ref(
            'generic_request.request_type_sequence'
        ).message_subscribe(self.request_demo_user.partner_id.ids)

        # Disable assets from uninstalled modules
        deactivate_records_for_model(self.env, 'ir.asset')

    def flush_tracking(self):
        """ Force the creation of tracking values. """
        self.env.flush_all()
        self.cr.precommit.run()

    @mute_logger('odoo.addons.mail.models.mail_mail',
                 'requests.packages.urllib3.connectionpool',
                 'odoo.models.unlink')
    def test_assign_employee(self):
        request = self.env['request.request'].with_context(
            mail_create_nolog=True,
            mail_notrack=True,
        ).create({
            'type_id': self.env.ref(
                'generic_request.request_type_sequence').id,
            'request_text': 'Test',
        })

        request.with_context(
            mail_notrack=False,
        ).write({
            'user_id': self.request_demo_user.id,
        })

        assign_messages = self.env['mail.mail'].search([
            ('model', '=', 'request.request'),
            ('res_id', '=', request.id),
            ('body_html', 'ilike',
             '%%You have been assigned to the request%%'),
        ])
        self.assertEqual(len(assign_messages), 1)

        self.authenticate(self.request_demo_user.login, 'demo')
        with mute_logger('odoo.addons.base.models.ir_model'):
            # Hide errors about missing menus
            res = self.url_open('/mail/view/request/%s' % request.id)
        self.assertEqual(res.status_code, 200)
        self.assertNotRegex(res.url, r'^%s/web/login.*$' % self.base_url())
        self.assertRegex(
            res.url, r'^%s/web#.*id=%s.*$' % (self.base_url(), request.id))

    @mute_logger('odoo.addons.mail.models.mail_mail',
                 'requests.packages.urllib3.connectionpool',
                 'odoo.models.unlink')
    def test_change_employee(self):
        origin_create = MailMail.create
        request = self.env['request.request'].with_user(
            self.request_demo_user
        ).with_context(
            mail_create_nolog=True,
            mail_notrack=True,
        ).create({
            'type_id': self.env.ref(
                'generic_request.request_type_sequence').id,
            'request_text': 'Test',
        })
        self.flush_tracking()

        request.message_subscribe(
            partner_ids=self.request_demo_user.partner_id.ids,
            subtype_ids=(
                self.env.ref('mail.mt_comment') +
                self.env.ref(
                    'generic_request.mt_request_stage_changed')
            ).ids)
        self.flush_tracking()

        def patch_create(self, vals):
            vals = dict(vals, auto_delete=False)
            return origin_create(self, vals)
        self.patch(MailMail, 'create', patch_create)
        request.with_user(self.user_root).with_context(
            mail_notrack=False,
        ).write({
            'stage_id': self.env.ref(
                'generic_request.'
                'request_stage_type_sequence_sent').id,
        })
        self.flush_tracking()

        messages = self.env['mail.mail'].search([
            ('model', '=', 'request.request'),
            ('res_id', '=', request.id),
            ('body_html', 'ilike',
             '%%/mail/view?model=request.request&amp;res_id=%s%%'
             % request.id),
        ])
        self.flush_tracking()  # TODO: Do we need it here?
        self.assertEqual(len(messages), 1)

        self.authenticate(self.request_demo_user.login, 'demo')
        with mute_logger('odoo.addons.base.models.ir_model'):
            # Hide errors about missing menus
            res = self.url_open('/mail/view/request/%s' % request.id)
        self.assertEqual(res.status_code, 200)
        self.assertNotRegex(res.url, r'^%s/web/login.*$' % self.base_url())
        self.assertRegex(
            res.url, r'^%s/web#.*id=%s.*$' % (self.base_url(), request.id))

    def test_subrequest_event_message(self):
        Request = self.env['request.request']
        simple_type = self.env.ref('generic_request.request_type_simple')

        # create parent request
        parent_request = Request.create({
            'type_id': simple_type.id,
            'category_id': self.env.ref(
                'generic_request.request_category_demo_general').id,
            'request_text': 'Parent test request'
        })

        # create child request
        with FindNew(self.env, 'request.request', 'mail.message') as nr:
            Request.create({
                'type_id': simple_type.id,
                'category_id': self.env.ref(
                    'generic_request.request_category_demo_general').id,
                'request_text': 'Parent test request',
                'parent_id': parent_request.id,
            })

        # check that child request created
        child_request = nr['request.request']
        self.assertTrue(child_request.exists())

        # assure that parent request has notification about child creation
        message = nr['mail.message'].filtered(
            lambda x: x.res_id == parent_request.id)
        message_text = re.sub('<.*?>', '', message.body)
        self.assertEqual(message_text,
                         'Subrequest %s of type %s has been created. '
                         % (child_request.name, child_request.type_id.name))

        # check that child_request not assigned
        self.assertFalse(child_request.user_id)

        # assign child request
        with FindNew(self.env, 'mail.message') as nr:
            child_request.action_request_assign_to_me()

        # assure that parent request has notification about child assignment
        message = nr['mail.message'].filtered(
            lambda x: x.res_id == parent_request.id)
        message_text = re.sub('<.*?>', '', message.body)
        self.assertEqual(message_text,
                         'Subrequest %s assigned to: %s. '
                         % (child_request.name, self.env.user.name))

        # change child request stage to 'sent'
        child_request.write({
            'stage_id': self.env.ref(
                'generic_request.request_stage_type_simple_sent').id
        })

        # change child request stage to 'rejected' (closed)
        with FindNew(self.env, 'mail.message') as nr:
            child_request.write({
                'stage_id': self.env.ref(
                    'generic_request.request_stage_type_simple_rejected').id
            })

        # assure that parent request has notification about child closing
        message = nr['mail.message'].filtered(
            lambda x: x.res_id == parent_request.id)
        message_text = re.sub('<.*?>', '', message.body)
        self.assertEqual(message_text,
                         'Subrequest %s has been closed. '
                         % child_request.name)

        # reopen closed child request
        with FindNew(self.env, 'mail.message') as nr:
            child_request.write({
                'stage_id': self.env.ref(
                    'generic_request.request_stage_type_simple_draft').id
            })

        # assure that parent request has notification about child reopening
        message = nr['mail.message'].filtered(
            lambda x: x.res_id == parent_request.id)
        message_text = re.sub('<.*?>', '', message.body)
        self.assertEqual(message_text,
                         'Subrequest %s has been reopened. '
                         % child_request.name)

    def test_deadline_track_changes_message(self):
        Request = self.env['request.request']
        simple_type = self.env.ref('generic_request.request_type_simple')
        date_today = fields.Date.today()
        datetime_today = fields.Datetime.now()

        # assure request type has deadline format 'date'
        self.assertEqual(simple_type.deadline_format, 'date')

        # create request
        deadline_request = Request.create({
            'type_id': simple_type.id,
            'category_id': self.env.ref(
                'generic_request.request_category_demo_general').id,
            'deadline_date': date_today,
            'request_text': 'Test deadline change message request'
        })
        field_deadline_date = self.env['ir.model.fields'].search([
            ('model_id', '=', deadline_request._name),
            ('name', '=', 'deadline_date')])
        field_deadline_date_dt = self.env['ir.model.fields'].search([
            ('model_id', '=', deadline_request._name),
            ('name', '=', 'deadline_date_dt')])
        self.flush_tracking()
        self.assertTrue(deadline_request.deadline_date)
        self.assertTrue(deadline_request.deadline_date_dt)

        # Change the deadline
        with FindNew(self.env, 'mail.message') as nr:
            deadline_request.deadline_date = date_today + relativedelta(days=6)
            self.flush_tracking()

        # Check message contains tracked field 'deadline_date'
        message = nr['mail.message']
        self.assertEqual(len(message), 1)
        message_tracked_field = message.tracking_value_ids.field_id
        self.assertEqual(len(message_tracked_field), 1)
        self.assertEqual(message_tracked_field, field_deadline_date)

        # Change deadline format to 'datetime'
        simple_type.deadline_format = 'datetime'
        # assure request type has deadline format 'datetime'
        self.assertEqual(simple_type.deadline_format, 'datetime')

        # Change request deadline
        with FindNew(self.env, 'mail.message') as nr:
            deadline_request.deadline_date_dt = datetime_today + relativedelta(
                hours=5)
            self.flush_tracking()

        # Check message contains tracked field 'deadline_date_dt'
        message = nr['mail.message']
        self.assertEqual(len(message), 1)
        message_tracked_field = message.tracking_value_ids.field_id
        self.assertEqual(len(message_tracked_field), 1)
        self.assertEqual(message_tracked_field, field_deadline_date_dt)
