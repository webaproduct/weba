from odoo import models, fields
from odoo.addons.generic_request.models.request_request import (
    TRACK_FIELD_CHANGES
)
from odoo.addons.generic_mixin import post_write


TRACK_FIELD_CHANGES.update(
    ['resource_id', 'resource_type_id', 'resource_res_id'])


class RequestRequest(models.Model):
    _name = "request.request"
    _inherit = [
        "request.request",
        "generic.resource.related.mixin",
    ]

    resource_required = fields.Boolean(
        related='classifier_id.resource_required', readonly=True)
    resource_invisible = fields.Boolean(
        related='classifier_id.resource_invisible', readonly=True)
    resource_res_id_domain = fields.Char(

    )

    resource_visible_on_form = fields.Boolean(
        default=False,
        help="Indicates whether the resource field should be visible "
             "on the form. "
             "This is a technical field used to determine visibility "
             "when no resources match the specified domain.")

    def _compute_service_category_type_domains(self):
        # flake8: noqa: E501
        # Required to set domain on resource_res_id
        res = super(
            RequestRequest, self)._compute_service_category_type_domains()

        for record in self:
            record.resource_res_id_domain = record._get_resource_res_id_domain()
        return res
    @post_write('resource_id')
    def _after_resource_id_changed(self, changes):
        self.trigger_event('resource-changed', {
            'old_resource_id': changes['resource_id'][0].id,
            'new_resource_id': changes['resource_id'][1].id,
        })

    def _get_resource_res_id_domain(self):
        """ This method returns domain for 'resource_res_id_domain' field
            in request, that related on resource type in classifier.
        """
        self.ensure_one()
        classifier = self.env['request.classifier'].search([
            ('service_id', '=', self.service_id.id),
            ('category_id', '=', self.category_id.id),
            ('type_id', '=', self.type_id.id),
        ])
        res_type = classifier.resource_type_id
        self.resource_res_model = res_type.model
        self.resource_type_id = res_type
        if res_type:
            self.resource_visible_on_form = True
        return [('id', 'in', res_type.resource_ids.ids)]
