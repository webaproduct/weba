from odoo import models, fields, _


class ProjectProject(models.Model):
    _inherit = "project.project"

    crm_lead_id = fields.Many2one(comodel_name="crm.lead", string="Opportunity")
    sales_manager_id = fields.Many2one(
        comodel_name="res.users", string="Sales Manager")
    project_month_id = fields.Many2one(comodel_name="project.month", string="Month")

    development_perspective = fields.Selection(
        selection=[
            ("not_defined", _("Not defined")),
            ("until_20", _("Until 20 hours")),
            ("20_50", _("20-50 hours")),
            ("50_100", _("50-100 hours")),
            ("more_100", _("More than 100 hours")),
            ("no", _("No")),
        ],
        string="Development perspective",
        default="not_defined",
    )

    # <---------Кнопка треков------------>
    total_timesheet = fields.Float(compute="_compute_total_timesheet")

    def _compute_total_timesheet(self):
        for rec in self:
            timesheets = self.env["account.analytic.line"].search(
                [("project_id", "=", rec.id)]
            )
            rec.total_timesheet = sum([record.unit_amount for record in timesheets])

    def action_total_timesheet(self):
        self.ensure_one()
        return {
            "name": _("Total timesheet"),
            "view_mode": "tree,kanban,pivot,graph",
            "res_model": "account.analytic.line",
            "type": "ir.actions.act_window",
            "domain": [("project_id", "=", self.id)],
            "context": {"default_project_id": self.id}
        }
    # <---------Кнопка треков------------>
