from odoo import models, fields


class RequestWizardChangeDeadline(models.TransientModel):
    _name = 'request.wizard.change.deadline'
    _description = 'Request Wizard: Change Deadline'

    request_id = fields.Many2one(
        'request.request', readonly=True, ondelete='cascade')
    request_deadline_format = fields.Selection(
        related='request_id.deadline_format')
    deadline_date = fields.Date('Deadline (date)')
    deadline_dt = fields.Datetime('Deadline (datetime)')
    deadline_change_reason_id = fields.Many2one(
        'request.deadline.change.reason', string='Change reason')
    deadline_change_comment = fields.Text(string='Comment')

    def action_change_deadline(self):
        self.ensure_one()
        request_values = {
            'deadline_last_change_reason_id':
                self.deadline_change_reason_id.id,
            'deadline_last_change_comment':
                self.deadline_change_comment,
        }
        if self.request_deadline_format == 'date':
            request_values.update({'deadline_date': self.deadline_date})
        else:
            request_values.update({'deadline_date_dt': self.deadline_dt})

        self.request_id.write(request_values)
