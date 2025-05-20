from odoo.addons.generic_request.tests.common import RequestCase
from odoo.addons.generic_mixin.tests.common import FindNew
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestGenericRequestTeamNotifications(RequestCase):

    @classmethod
    def setUpClass(cls):
        super(TestGenericRequestTeamNotifications, cls).setUpClass()
        cls.team_1 = cls.env.ref('generic_team.generic_team_team1')
        cls.team_2 = cls.env.ref('generic_team.generic_team_team2')

    def test_assign_team_default_notification(self):
        self.assertEqual(self.request_1.type_id, self.simple_type)

        # Assign request to team
        team = self.team_1
        AssignWizard = self.env['request.wizard.assign']
        assign_wizard = AssignWizard.sudo().create({
            'team_id': team.id,
            'request_ids': [(6, 0, self.request_1.ids)],
        })

        self.assertFalse(assign_wizard.user_id)
        self.assertEqual(assign_wizard.team_id, team)
        with FindNew(self.env, 'mail.mail') as nr:
            assign_wizard.do_assign()
        assign_event = self._get_last_event(self.request_1)
        self.assertEqual(assign_event.event_code, 'team-assigned')

        # Check all team members received emails
        assign_mail = nr['mail.mail']
        team_members = team.user_ids | team.leader_id
        self.assertEqual(len(assign_mail), 1)

        # Check mails contains correct subject
        notification_subject = 'Your team has received a new request %s!' \
                               % self.request_1.name
        mail_subject = assign_mail.subject
        self.assertTrue(notification_subject == mail_subject)

        # Check mail recipients
        self.assertEqual(len(team_members), len(assign_mail.partner_ids))
        self.assertEqual(team_members.mapped('partner_id'),
                         assign_mail.partner_ids)

        # Disable default notification for team assignment
        classifier = self.request_1.classifier_id
        classifier.send_mail_on_request_team_assigned_event = False
        self.env.invalidate_all()

        # Reassign team
        team2 = self.team_2
        AssignWizard = self.env['request.wizard.assign']
        assign_wizard = AssignWizard.sudo().create({
            'team_id': team2.id,
            'request_ids': [(6, 0, self.request_1.ids)],
        })

        self.assertFalse(assign_wizard.user_id)
        self.assertEqual(assign_wizard.team_id, team2)
        with FindNew(self.env, 'mail.message') as nr:
            assign_wizard.do_assign()
        assign_event = self._get_last_event(self.request_1)
        self.assertEqual(assign_event.event_code, 'team-reassigned')

        # Check team members didn't receive emails
        assign_notifications = nr['mail.message']
        team_members = team2.user_ids | team2.leader_id
        self.assertEqual(len(team_members), 4)
        mails = assign_notifications.filtered(
            lambda x: x.message_type == 'notification')
        self.assertFalse(mails)
