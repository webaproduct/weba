from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    resource_required = fields.Boolean(
        'Resource is required',
        help='Set this checkbox to make resource field required '
             'on requests of this classifier')
    resource_invisible = fields.Boolean(
        'Hide resource fields',
        help='Hide resource fields on request form view, '
             'when this classifier is selected')

    resource_type_id = fields.Many2one(
        'generic.resource.type',
        string="Resource type",
        help="Resource type allowed for selection on requests of this type.")
