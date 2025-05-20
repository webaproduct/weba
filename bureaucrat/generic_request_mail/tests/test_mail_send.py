import logging

from odoo.addons.generic_request.tests.common import RequestCase

_logger = logging.getLogger(__name__)


class TestRequestSendSettings(RequestCase):

    @classmethod
    def setUpClass(cls):
        super(TestRequestSendSettings, cls).setUpClass()

        cls.env['ir.config_parameter'].set_param(
            "mail.catchall.domain", "example.com")
        cls.mail_source = cls.env.ref(
            'generic_request_mail.demo_request_mail_source')

        cls.partner_1 = cls.env['res.partner'].with_context(
            mail_create_nolog=True,
            mail_create_nosubscribe=True,
            mail_notrack=True,
            no_reset_password=True,
        ).create({
            'name': 'Valid Lelitre',
            'email': 'valid.lelitre@agrolait.com',
        })

    def test_request_mailing_config_no_mail_source_on_request(self):
        _sent_emails = []

        def send_email(self, message, mail_server_id=None, smtp_server=None,
                       smtp_port=None, smtp_user=None, smtp_password=None,
                       smtp_encryption=None, smtp_debug=False,
                       smtp_session=None):
            _sent_emails.append(
                (mail_server_id, message)
            )
            return message['Message-Id']

        self.patch(type(self.env['ir.mail_server']), 'send_email', send_email)
        # If mail source is not specified on request,
        # then all messages have to go in standard way:
        # sent via user's email
        request = self.env['request.request'].with_context(
            mail_notify_force_send=True,
        ).with_user(self.request_manager).create({
            'author_id': self.partner_1.id,
            'type_id': self.simple_type.id,
            'request_text': 'Test Request',
        })
        mail = self.env['mail.mail'].search([
            ('model', '=', 'request.request'),
            ('res_id', '=', request.id)])
        mail.send()
        self.assertFalse(request.mail_source_id)

        self.assertEqual(len(_sent_emails), 1)
        last_mail_srv, _ = _sent_emails[-1]
        self.assertFalse(last_mail_srv)

        # These mail parameters (From, Reply-To, To)
        # can be customized by users in the mail template,
        # so there's no strict need to test them at this stage.
        # self.assertEqual(
        #     last_mail_msg['From'],
        #     'Demo Request Manager <demo-request-manager@demo.demo>')
        # self.assertEqual(
        #     last_mail_msg['Reply-To'],
        #     'YourCompany <catchall@example.com>')
        # self.assertEqual(
        #     last_mail_msg['To'],
        #     '"Valid Lelitre" <valid.lelitre@agrolait.com>')

        request.with_context(
            mail_notify_force_send=True
        ).message_post(
            body="Test Message",
            subtype_id=self.env.ref('mail.mt_comment').id)
        self.assertEqual(len(_sent_emails), 2)
        last_mail_srv, _ = _sent_emails[-1]
        self.assertFalse(last_mail_srv)

        # These mail parameters (From, Reply-To, To)
        # can be customized by users in the mail template,
        # so there's no strict need to test them at this stage.
        # self.assertEqual(
        #     last_mail_msg['From'],
        #     'Demo Request Manager <demo-request-manager@demo.demo>')
        # self.assertEqual(
        #     last_mail_msg['Reply-To'],
        #     'YourCompany <catchall@example.com>')
        # self.assertEqual(
        #     last_mail_msg['To'],
        #     '"Valid Lelitre" <valid.lelitre@agrolait.com>')

    def test_request_mailing_config_default_mail_source_on_request(self):
        _sent_emails = []

        def send_email(self, message, mail_server_id=None, smtp_server=None,
                       smtp_port=None, smtp_user=None, smtp_password=None,
                       smtp_encryption=None, smtp_debug=False,
                       smtp_session=None):
            _sent_emails.append(
                (mail_server_id, message)
            )
            return message['Message-Id']

        self.patch(type(self.env['ir.mail_server']), 'send_email', send_email)
        # If default mail source configured, then it have to be automatically
        # set on created requests, and also, if mailsource selected,
        # then mailsource address have to be set as 'email_from' header for all
        # messages
        self.env['ir.config_parameter'].set_param(
            'generic_request_mail.default_mail_source_id',
            self.mail_source.id)

        request = self.env['request.request'].with_context(
            mail_notify_force_send=True,
        ).with_user(self.request_manager).create({
            'author_id': self.partner_1.id,
            'type_id': self.simple_type.id,
            'request_text': 'Test Request',
        })
        self.assertEqual(request.mail_source_id, self.mail_source)

        mail = self.env['mail.mail'].search([
            ('model', '=', 'request.request'),
            ('res_id', '=', request.id)])
        mail.send()
        self.assertEqual(len(_sent_emails), 1)
        last_mail_srv, _ = _sent_emails[-1]
        self.assertFalse(last_mail_srv)

        # These mail parameters (From, Reply-To, To)
        # can be customized by users in the mail template,
        # so there's no strict need to test them at this stage.
        # self.assertEqual(
        #     last_mail_msg['From'],
        #     'YourCompany Demo Requests '
        #     '<demo-requests@example.com>')
        # self.assertEqual(
        #     last_mail_msg['Reply-To'],
        #     'YourCompany Demo Requests '
        #     '<demo-requests@example.com>')
        # self.assertEqual(
        #     last_mail_msg['To'],
        #     '"Valid Lelitre" <valid.lelitre@agrolait.com>')

        request.with_context(
            mail_notify_force_send=True
        ).message_post(
            body="Test Message",
            subtype_id=self.env.ref('mail.mt_comment').id)
        self.assertEqual(len(_sent_emails), 2)
        last_mail_srv, _ = _sent_emails[-1]
        self.assertFalse(last_mail_srv)
        # These mail parameters (From, Reply-To, To)
        # can be customized by users in the mail template,
        # so there's no strict need to test them at this stage.
        # self.assertEqual(
        #     last_mail_msg['From'],
        #     'YourCompany Demo Requests '
        #     '<demo-requests@example.com>')
        # self.assertEqual(
        #     last_mail_msg['Reply-To'],
        #     'YourCompany Demo Requests '
        #     '<demo-requests@example.com>')
        # self.assertEqual(
        #     last_mail_msg['To'],
        #     '"Valid Lelitre" <valid.lelitre@agrolait.com>')
