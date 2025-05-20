from odoo import http


class WebsiteExtraTagController(http.Controller):
    @http.route(["/api/get_tags"], type='json', auth='public')
    def get_tags(self, **post):
        req_tag_categories = http.request.env['generic.tag.category'].sudo(
        ).search([])
        return self.get_tags_data(req_tag_categories)

    @staticmethod
    def get_tags_data(tag_categories):
        data = [{
            "id": tag_category.id,
            "code": tag_category.code,
            "name": tag_category.display_name,
            "tags": [{
                "id": tag.id,
                "name": tag.name,
            } for tag in tag_category.tag_ids]
        } for tag_category in tag_categories]
        return data
