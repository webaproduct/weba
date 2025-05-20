import datetime
import ast

import logging
import defusedxml.ElementTree as ET

from odoo import http, fields
from odoo.addons.crnd_vsd.controllers.api import WebsiteRequest

_logger = logging.getLogger(__name__)


class WebsiteRequestFieldSet(WebsiteRequest):
    def _request_new_prepare_data(self, **post):
        res = super()._request_new_prepare_data(**post)
        req_data = post.get('requestData')

        for key, value in req_data.items():
            try:
                if 'fieldset_' not in key:
                    continue

                request_classifier = http.request.env[
                    'request.classifier'].get_classifiers(
                    service=res.get("service_id"),
                    category=res.get("category_id"),
                    request_type=res.get("type_id"),
                    limit=1
                )
                field_set_model = (request_classifier.field_set_type_id
                                   .field_set_model_id)
                clean_key = key.replace('fieldset_', '')
                field_type = field_set_model.field_id.filtered(
                    lambda x: x.name == clean_key).ttype

                if field_type == 'date':
                    if value:
                        res[key] = fields.Datetime.to_string(
                            datetime.datetime.fromisoformat(value)
                        )
                elif field_type == 'datetime':
                    if value:
                        res[key] = fields.Datetime.to_string(
                            datetime.datetime.fromisoformat(value)
                        )
                elif field_type == 'many2one':
                    res[key] = int(value)

                elif field_type == 'many2many':
                    m2m_values = [int(val) for val in value if val]
                    res[key] = [(6, 0, m2m_values)] if m2m_values else [(5,)]
                else:
                    res[key] = value
            except Exception as e:
                _logger.debug(f'Cannot convert fieldset values: {e}')

        return res

    def _get_template_data(self, req_service, req_category, req_type, **post):
        # pylint: disable=too-many-locals
        data = super()._get_template_data(
            req_service, req_category, req_type, **post)

        request_classifier = http.request.env[
            'request.classifier'
        ].get_classifiers(
            service=req_service.id if req_service else None,
            category=req_category.id if req_category else None,
            request_type=req_type.id if req_type else None,
            limit=1
        )

        if not request_classifier:
            return data

        field_set_type = request_classifier.sudo().field_set_type_id
        field_set_model = field_set_type.sudo().field_set_model_id

        field_set_form_view = field_set_model.view_ids.filtered(
            lambda x: x.type == 'form'
        )

        if not field_set_form_view:
            return data

        tree = ET.fromstring(field_set_form_view.arch)
        all_fields_elements = tree.findall('.//field')
        all_fields_elements_names = [
            x.attrib.get('name')
            for x in all_fields_elements
        ]

        data['field_set'] = []
        data['field_set_option_list'] = {}

        for field_name in all_fields_elements_names:
            field = field_set_model.field_id.filtered(
                lambda x: x.name == field_name
            )
            if not field or field.readonly:
                continue

            resp_data = {
                'id': field.id,
                'name': field.name,
                'field_type': field.ttype,
                'display_name': field.field_description,
                'required': field.required,
                'values': [],
            }

            if field.ttype == 'selection':
                for val_rec in field.selection:
                    resp_data['values'].append({
                        "value": val_rec[0],
                        "name": val_rec[1],
                    })

            elif field.ttype in ['many2many', 'many2one']:
                if isinstance(field.domain, str):
                    domain = ast.literal_eval(field.domain) or []
                else:
                    domain = field.domain or []
                value_records = http.request.env[field.relation].search(domain)
                for val_rec in value_records:
                    resp_data['values'].append({
                        "name": val_rec.display_name,
                        "value": val_rec.id,
                    })

            data['field_set'].append(resp_data)

        return data

    def get_single_request_data(self, req):
        data = super().get_single_request_data(req)
        if not req.classifier_id.read_show_field_set:
            return data

        data['field_set'] = []

        field_set_model = req.sudo().field_set_model_id
        field_set_form_view = field_set_model.view_ids.filtered(
            lambda x: x.type == 'form'
        )
        if not field_set_form_view:
            return data

        field_set_rec = http.request.env[req.field_set_model_name].sudo(
        ).search([
            ["request_id", "=", req.id],
        ])
        if not field_set_rec:
            return data

        tree = ET.fromstring(field_set_form_view.arch)
        all_fields_elements = tree.findall('.//field')
        all_fields_elements_names = [
            x.attrib.get('name')
            for x in all_fields_elements
        ]

        for field_name in all_fields_elements_names:
            if field_name == 'request_id':
                continue

            field = field_set_model.field_id.filtered(
                lambda x: x.name == field_name
            )
            if not field or field.readonly:
                continue

            field_set_field_data = {
                'name': field.name,
                'field_type': field.ttype,
                'display_name': field.field_description,
                'values': [],
            }

            if field.ttype in ['many2many', 'many2one']:
                value_records = getattr(field_set_rec, field_name)
                for val_rec in value_records:
                    field_set_field_data['values'].append(val_rec.display_name)
            elif field.ttype in ['date', 'datetime']:
                field_set_field_data['values'] = [
                    self._get_datetime_field_value(
                        getattr(field_set_rec, field_name))
                ]
            else:
                field_set_field_data['values'] = [
                    getattr(field_set_rec, field_name)
                ]

            data['field_set'].append(field_set_field_data)

        return data
