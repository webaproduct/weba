from odoo import models, fields, _, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    partner_id_source_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    telegram = fields.Char(string="Telegram")

    """Конвертація у нагоду"""
    def _handle_partner_assignment(self, force_partner_id=False, create_missing=True):
        for lead in self:
            if force_partner_id:
                lead.partner_id = force_partner_id
            if not lead.partner_id and create_missing:
                partner = lead._create_customer()
                lead.partner_id = partner.id

                # Custom
                partner.write({
                    "telegram": lead.telegram,
                    "source_id": lead.source_id.id,
                    "partner_id_source_id": lead.partner_id_source_id.id
                })

    @api.onchange("partner_id")
    def _onchange_source_id_partner_id_source_id(self):
        self.ensure_one()
        if self.type == "opportunity" and self.partner_id:
            self.source_id = self.partner_id.source_id.id
            self.partner_id_source_id = self.partner_id.partner_id_source_id.id

    project_month_id = fields.Many2one(
        comodel_name="project.month", string="Expected closing")

    # <----------------Предоплата - Пост оплата--------------------->
    hours = fields.Float(string="Hours")
    payment_percentage = fields.Integer(string="Payment percentage")
    subscription = fields.Float(string="Subscription")
    postpaid = fields.Float(string="Postpaid")
    bonus = fields.Text(string="Bonus")

    @api.onchange("payment_percentage", "expected_revenue")
    def _onchange_payment_percentage(self):
        self.ensure_one()
        if self.expected_revenue and self.payment_percentage:
            subscription = self.expected_revenue * (self.payment_percentage / 100)

            self.subscription = subscription
            self.postpaid = self.expected_revenue - subscription
        else:
            self._onchange_subscription()
            self._onchange_postpaid()

    @api.onchange("subscription")
    def _onchange_subscription(self):
        self.ensure_one()
        if self.expected_revenue and self.subscription:
            self.postpaid = self.expected_revenue - self.subscription

    @api.onchange("postpaid")
    def _onchange_postpaid(self):
        self.ensure_one()
        if self.expected_revenue and self.postpaid:
            self.subscription = self.expected_revenue - self.postpaid

    # <------------------------------------------->

    # <---------Кнопка проектов------------>

    count_projects = fields.Integer(compute="_compute_count_project")

    def _compute_count_project(self):
        for rec in self:
            count_project = self.env["project.project"].search_count(
                [("crm_lead_id", "=", rec.id)]
            )
            rec.count_projects = count_project

    def action_view_projects(self):
        self.ensure_one()

        return {
            "name": _("Project"),
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "target": "current",
            "view_mode": "tree,form",
            "domain": [("crm_lead_id", "=", self.id)],
            "context": {
                "default_name": self.name,
                "default_crm_lead_id": self.id,
                "default_sales_manager_id": self.user_id.id,
            },
        }
    # <---------Кнопка проектов------------>
