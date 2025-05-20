from odoo import models, fields


class Agreement(models.Model):
    _name = "agreement"
    _description = "Agreement"

    name = fields.Char(string="Name")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact")
