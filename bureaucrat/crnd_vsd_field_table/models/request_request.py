from odoo import models, api


class RequestRequest(models.Model):
    _inherit = [
        'request.request'
    ]

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            fieldset_values = {}

            for name, value in list(vals_list.items()):
                if 'fieldset_' in name:
                    fieldset_values[name.replace('fieldset_', '')] = value
                    del vals_list[name]

            req = super().create(vals_list)
            if fieldset_values:
                self.fieldset_creation(fieldset_values, req)
            return req

        records = self.browse()

        for vals in vals_list:
            fieldset_values = {}
            for name, value in list(vals.items()):
                if 'fieldset_' in name:
                    fieldset_values[name.replace('fieldset_', '')] = value
                    del vals[name]

            req = super().create(vals)
            if fieldset_values:
                self.fieldset_creation(fieldset_values, req)

            records |= req
        return records

    def fieldset_creation(self, vals_list, request):
        fieldset = request.field_set_values_record
        if isinstance(fieldset, bool) and not fieldset:
            return

        if not fieldset:
            # create
            vals_list['request_id'] = request.id
            fieldset.create(vals_list)

        # update
        fieldset.write(vals_list)
