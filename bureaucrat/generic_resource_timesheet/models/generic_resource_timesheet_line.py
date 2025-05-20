from odoo import models, fields, api
from odoo.addons.generic_m2o import generic_m2o_get


class GenericResourceTimesheetLine(models.Model):
    _name = 'generic.resource.timesheet.line'
    _inherit = [
        'generic.resource.related.mixin',
    ]
    _description = 'Generic Resource Timesheet Line'
    _order = "date_start DESC"

    date_start = fields.Datetime(
        index=True, required=True,
        default=fields.Datetime.now)
    date_stop = fields.Datetime(index=True, required=True)
    activity_id = fields.Many2one(
        'generic.resource.timesheet.activity',
        ondelete='restrict', index=True,
        required=True, string='Activity')

    doc_model = fields.Char(
        related='activity_id.model_id.model',
        readonly=True, store=True, index=True)
    doc_id = fields.Many2oneReference(
        string='Document', index=True, model_field='doc_model',
        help="Document that have generated this line.")

    color = fields.Char(related='activity_id.color')

    @api.depends('display_name')
    def _compute_display_name(self):
        for record in self:
            document = record.get_document()
            if document:
                current_name = (record.id, '%s: %s (%s)'
                                % (record.resource_id.display_name,
                                   record.activity_id.display_name,
                                   document.display_name))
            else:
                current_name = (record.id, '%s: %s'
                                % (record.resource_id.display_name,
                                   record.activity_id.display_name))

            record.display_name = current_name

        return True

    def get_document(self):
        self.ensure_one()
        if self.activity_id and self.doc_id:
            return generic_m2o_get(
                self, field_res_model='doc_model', field_res_id='doc_id')
        return False
