from odoo import models, fields


class TestIncidentFieldTable(models.Model):
    _name = 'test.incident.field.table.value'
    _description = 'Test: Incident Field Table Value'
    _inherit = [
        'generic.request.field.table.mixin',
    ]

    char_1 = fields.Char()
    integer_1 = fields.Integer()
    float_1 = fields.Float()
    date_1 = fields.Date()
    datetime_1 = fields.Datetime()
    many2one_1_id = fields.Many2one('res.partner')
    many2many_1_ids = fields.Many2many('res.partner')
