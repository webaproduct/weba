from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    number = fields.Char(string="№")
    organization_id = fields.Many2one(
        comodel_name="account.journal",
        string="Organization",
        domain="[('id', 'in', (22, 24, 25, 26, 27, 28, 29))]"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["number"] = self.env["ir.sequence"].next_by_code(
                "numbering.number.account.move")
        return super(AccountMove, self).create(vals_list)
