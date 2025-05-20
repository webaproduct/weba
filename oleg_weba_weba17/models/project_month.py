import datetime

from odoo import models, fields, _, api


class ProjectMonth(models.Model):
    _name = "project.month"
    _description = "Project Month"
    _rec_names_search = ["month", "year"]

    def _compute_display_name(self):
        for rec in self:
            month = dict(rec._fields["month"]._description_selection(self.env)).get(
                rec.month)

            rec.display_name = f"{month} {rec.year}"

    # Для сохранения отображаемого названия записи под язык пользователя
    display_name_store = fields.Char(compute="_compute_display_name_store", store=True)

    @api.depends("display_name")
    def _compute_display_name_store(self):
        for rec in self:
            rec.display_name_store = rec.display_name

    month = fields.Selection(
        selection=[
            ("january", _("January")),
            ("february", _("February")),
            ("march", _("March")),
            ("april", _("April")),
            ("may", _("May")),
            ("june", _("June")),
            ("july", _("July")),
            ("august", _("August")),
            ("september", _("September")),
            ("october", _("October")),
            ("november", _("November")),
            ("december", _("December")),
        ],
        string="Month",
        required=True,
    )
    year = fields.Char(string="Year", default=datetime.date.today().year, required=True)
