from odoo import models, exceptions


class GenericResourceRelatedMixin(models.AbstractModel):
    _inherit = 'generic.resource.related.mixin'

    def _inverse_resource_res_id(self):
        # pylint: disable=missing-return
        try:
            super()._inverse_resource_res_id()
        except exceptions.ValidationError as e:
            if self._name == 'request.request':
                for rec in self:
                    if not rec.resource_res_id:
                        rec.resource_type_id = False
                    else:
                        raise e
            else:
                raise e
