from odoo import models


class Currency(models.Model):
    _inherit = "res.currency"

    def amount_to_text(self, amount):
        return super(Currency, self).amount_to_text(amount).capitalize()
