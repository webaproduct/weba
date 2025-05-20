from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    agreement_id = fields.Many2one(
        comodel_name="agreement",
        string="Agreement",
        domain="['|', ('partner_id', '=', id), ('id', '=', 2)]"
    )
    name_initials = fields.Char(string="Name initials")
    ref = fields.Char(string="Is a tax payer", index=True)
    telegram = fields.Char(string="Telegram")
    source_id = fields.Many2one(comodel_name="utm.source", string="Source")
    partner_id_source_id = fields.Many2one(comodel_name="res.partner", string="Partner")
