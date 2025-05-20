import datetime
import ast

import logging
import defusedxml.ElementTree as ET

from odoo import http, fields
from odoo.addons.crnd_vsd.controllers.api import WebsiteRequest

_logger = logging.getLogger(__name__)


class WebsiteRequestFieldSet(WebsiteRequest):

    # pylint: disable=too-many-nested-blocks
    def _request_post_create_data(self, req, **post):
        super()._request_post_create_data(req, **post)
        req_data = post.get('requestData')

        if 'fieldtable' in req_data:
            try:
                request_classifier = req.classifier_id
                field_table_model = (request_classifier.field_table_type_id
                                     .field_table_model_id)

                for row in req_data.get('fieldtable'):
                    row_create_data = {
                        "request_id": req.id,
                    }
                    for key, value in row.items():
                        clean_key = key.replace('fieldtable_', '')
                        field_type = field_table_model.field_id.filtered(
                            lambda x: x.name == clean_key).ttype

                        if field_type == 'date':
                            if value:
                                row_create_data[clean_key] = (
                                    fields.Datetime.to_string(
                                        datetime.datetime.fromisoformat(value)
                                    )
                                )
                        elif field_type == 'datetime':
                            if value:
                                row_create_data[clean_key] = (
                                    fields.Datetime.to_string(
                                        datetime.datetime.fromisoformat(value)
                                    )
                                )
                        elif field_type == 'many2one':
                            row_create_data[clean_key] = int(value)

                        elif field_type == 'many2many':
                            m2m_values = [int(val) for val in value if val]
                            row_create_data[clean_key] = [(6, 0, m2m_values)] \
                                if m2m_values else [(5,)]
                        else:
                            row_create_data[clean_key] = value

                    http.request.env[field_table_model.model].create(
                        row_create_data)
            except Exception as e:
                _logger.debug(f'Cannot convert fieldset values: {e}')

        return True

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

        field_table_type = request_classifier.sudo().field_table_type_id
        field_table_model = field_table_type.sudo().field_table_model_id

        field_table_form_view = field_table_model.view_ids.filtered(
            lambda x: x.type == 'form'
        )

        if not field_table_form_view:
            return data

        tree = ET.fromstring(field_table_form_view.arch)
        all_fields_elements = tree.findall('.//field')
        all_fields_elements_names = [
            x.attrib.get('name')
            for x in all_fields_elements
        ]

        data['field_table'] = []
        data['field_table_name'] = field_table_model.name
        data['field_table_option_list'] = {}

        for field_name in all_fields_elements_names:
            field = field_table_model.field_id.filtered(
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

            data['field_table'].append(resp_data)
        return data

    # pylint: disable=too-many-locals
    def get_single_request_data(self, req):
        data = super().get_single_request_data(req)
        if not req.classifier_id.read_show_field_table:
            return data

        data['field_table'] = []

        field_table_model = req.sudo().field_table_model_id
        field_table_form_view = field_table_model.view_ids.filtered(
            lambda x: x.type == 'form'
        )
        if not field_table_form_view:
            return data

        data['field_table_model_name'] = field_table_model.name

        field_table_rec = http.request.env[req.field_table_model_name].sudo(
        ).search([
            ["request_id", "=", req.id],
        ])
        if not field_table_rec:
            return data

        tree = ET.fromstring(field_table_form_view.arch)
        all_fields_elements = tree.findall('.//field')
        all_fields_elements_names = [
            x.attrib.get('name')
            for x in all_fields_elements
        ]

        for rec in field_table_rec:
            field_table_row = []
            for field_name in all_fields_elements_names:
                if field_name == 'request_id':
                    continue

                field = field_table_model.field_id.filtered(
                    lambda x: x.name == field_name
                )
                if not field or field.readonly:
                    continue

                field_table_field_data = {
                    'name': field.name,
                    'field_type': field.ttype,
                    'display_name': field.field_description,
                    'values': [],
                }

                if field.ttype in ['many2many', 'many2one']:
                    value_records = getattr(rec, field_name)
                    for val_rec in value_records:
                        field_table_field_data['values'].append(
                            val_rec.display_name)
                elif field.ttype in ['date', 'datetime']:
                    field_table_field_data['values'] = [
                        self._get_datetime_field_value(
                            getattr(rec, field_name))
                    ]
                else:
                    field_table_field_data['values'] = [
                        getattr(rec, field_name)
                    ]
                field_table_row.append(field_table_field_data)
            data['field_table'].append(field_table_row)

        return data
