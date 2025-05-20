from odoo import models, fields, api


class RequestWizardResponsible(models.TransientModel):
    _name = 'request.wizard.responsible'
    _description = 'Request Wizard: Set responsible'

    def _default_user_id(self):
        return self.env.user

    def _default_unsubscribe(self):
        company = self.env.user.company_id
        return company.request_autoset_unsubscribe_prev_responsible

    request_ids = fields.Many2many(
        'request.request', string='Requests', required=True)
    responsible_id = fields.Many2one(
        'res.users',
        string="User",
        default=_default_user_id,
        required=True,
        ondelete='cascade')
    partner_id = fields.Many2one(
        'res.partner', related="responsible_id.partner_id",
        readonly=True, store=False)
    comment = fields.Text()
    unsubscribe_prev_responsible = fields.Boolean(
        default=_default_unsubscribe,
        string='Unsubscribe previously responsible')
    # Technical field
    show_field_unsubscribe = fields.Boolean(
        compute='_compute_show_unsubscribe_field')

    @api.onchange('request_ids')
    def _compute_show_unsubscribe_field(self):
        for rec in self:
            rec.show_field_unsubscribe = any([
                bool(r.responsible_id) for r in rec.request_ids])

    def _prepare_set_responsible(self):
        """ Prepare data for set responsibility

            This method have to prepare dict with data to be written to request
        """
        self.ensure_one()
        return {
            'responsible_id': self.responsible_id.id,
        }

    def _do_responsibility_implementation(self, request):
        self.ensure_one()
        request.with_context(
            responsible_comment=self.comment
        ).write(self._prepare_set_responsible())

    def _do_set_responsible(self, request):
        prev_responsible = request.responsible_id
        self._do_responsibility_implementation(request)
        if self.comment:
            request.message_post(body=self.comment)

        new_responsible = request.responsible_id
        if (self.unsubscribe_prev_responsible and prev_responsible
                and new_responsible != prev_responsible):
            request._close_mail_activities_for_user(prev_responsible)
            request.message_unsubscribe(
                partner_ids=prev_responsible.partner_id.ids)

    def do_set_responsible(self):
        self.ensure_one()
        self.request_ids.ensure_can_set_responsible()
        for request in self.request_ids:
            self._do_set_responsible(request)
