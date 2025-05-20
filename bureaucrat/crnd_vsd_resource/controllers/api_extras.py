from odoo import http


class WebsiteExtraTagController(http.Controller):
    @http.route(["/api/get_resource_type/<int:resource_type_id>"],
                type='json', auth='public')
    def get_resource_type(self, resource_type_id, **post):
        resource_type = http.request.env['generic.resource.type'].sudo(
        ).browse(resource_type_id)
        return self.get_resource_data(resource_type)

    @staticmethod
    def get_resource_data(resource_type):
        data = {
            "id": resource_type.id,
            "code": resource_type.code,
            "name": resource_type.display_name,
            "resources": [{
                "id": resource.id,
                "name": resource.display_name,
            } for resource in resource_type.resource_ids]
        }
        return data
