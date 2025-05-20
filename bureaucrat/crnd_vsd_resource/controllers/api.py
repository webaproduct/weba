from odoo.addons.crnd_vsd.controllers.api import WebsiteRequest


class WebsiteRequestResource(WebsiteRequest):
    def _request_new_prepare_data(self, **post):
        res = super()._request_new_prepare_data(**post)
        req_data = post.get('requestData')

        res['resource_id'] = req_data.get('resource_id')
        return res

    def get_single_request_data(self, req):
        data = super().get_single_request_data(req)
        if req.classifier_id.read_show_resource:
            data.update({
                "resource": {
                    "id": req.resource_id.id,
                    "name": req.resource_id.display_name,
                } if req.resource_id else None
            })
        return data
