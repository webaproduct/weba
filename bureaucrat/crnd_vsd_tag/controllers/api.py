from odoo import http
from odoo.addons.crnd_vsd.controllers.api import WebsiteRequest


class WebsiteRequestTags(WebsiteRequest):
    def _request_new_prepare_data(self, **post):
        res = super()._request_new_prepare_data(**post)
        req_data = post.get('requestData')

        req_tag_ids = res['tag_ids'] = []
        tags_code_list = [
            x.replace('tag_', '') for x in req_data.keys() if 'tag_' in x
        ]
        req_tag_categories = http.request.env['generic.tag.category'].sudo(
        ).search([
            ["code", "in", tags_code_list]
        ])

        tag_ids = []
        for tag_category in req_tag_categories:
            tag_values = req_data.get(f'tag_{tag_category.code}')
            if tag_category.check_xor:
                if not isinstance(tag_values, list):
                    tag_ids.append(tag_values)
            else:
                if isinstance(tag_values, list):
                    tag_ids.extend(tag_values)

        req_tag_ids.append((6, 0, tag_ids))

        return res

    def _get_template_data(self, req_service, req_category, req_type, **post):
        data = super()._get_template_data(
            req_service, req_category, req_type, **post)

        req_tag_categories = self._get_req_tag_categories(
            req_type=req_type,
            req_category=req_category if req_category else None,
            req_service=req_service if req_service else None)

        data['request_tag_categories'] = req_tag_categories
        return data

    def _get_req_tag_categories(self, req_type, req_category, req_service):
        """
        Retrieve tag category recordset associated with the given request
        classifiers.

        Parameters:
        - req_type (RequestType): The request type object.
        - req_category (RequestCategory or None):
            The request category object or None.
        - req_service (RequestService or None):
            The request service object or None.

        Returns:
        recordset: A recordset of tag category IDs associated with the provided
        request classifiers.
        """
        classifier = http.request.env['request.classifier'].sudo().search([
            ('type_id', '=', req_type.id),
            ('category_id', '=', req_category.id),
            ('service_id', '=', req_service.id if req_service else False)
        ])
        tag_categories = classifier.tag_category_ids
        return tag_categories

    def get_single_request_data(self, req):
        data = super().get_single_request_data(req)
        if req.classifier_id.read_show_tags:
            data.update({
                "tags": [
                    {
                        "id": tag.id,
                        "name": tag.display_name,
                        "color": tag.color,
                    } for tag in req.tag_ids
                ]
            })
        return data

    def _get_additional_filter(self, filter_item, res_model) -> list:
        result = super()._get_additional_filter(filter_item, res_model)
        if 'tag_' in filter_item.get('name'):
            result.append((
                'tag_ids', 'in', filter_item.get("value")
            ))
        return result
