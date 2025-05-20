from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    location_required = fields.Boolean(
        'Location is required',
        help='Set this checkbox to make location field required '
             'on requests of this classifier')
    location_invisible = fields.Boolean(
        'Hide location fields',
        help='Hide location fields on request form view, '
             'when this classifier is selected')
