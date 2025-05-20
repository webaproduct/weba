from odoo import models, fields


class GenericTagCategory(models.Model):
    _inherit = "generic.tag.category"

    classifier_ids = fields.Many2many(
        'request.classifier', 'request_classifier_tag_category_rel',
        'category_id', 'classifier_id', string='Request Classifiers',
        readonly=True
    )
