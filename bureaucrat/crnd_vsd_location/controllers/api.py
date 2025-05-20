from odoo import http
from odoo.addons.crnd_vsd.controllers.api import WebsiteRequest


class WebsiteRequestLocation(WebsiteRequest):
    def _request_new_prepare_data(self, **post):
        res = super()._request_new_prepare_data(**post)
        req_data = post.get('requestData')

        res['generic_location_id'] = req_data.get('generic_location_id')
        return res

    def _get_template_data(self, req_service, req_category, req_type, **post):
        data = super()._get_template_data(
            req_service, req_category, req_type, **post)
        data['locations'] = http.request.env['generic.location'].sudo(
        ).search([])
        return data

    def get_single_request_data(self, req):
        data = super().get_single_request_data(req)
        if req.classifier_id.read_show_location:
            data.update({
                "location": {
                    "id": req.generic_location_id.id,
                    "name": req.generic_location_id.display_name,
                } if req.generic_location_id else None
            })
        return data
