from odoo import http
from odoo.http import request

from odoo.addons.yodoo_knowledge_website.controllers.api import (
    WebsiteKnowledge)


class WebsiteKnowledgeBusinessDomain(WebsiteKnowledge):
    @http.route([
        '/yodoo_knowledge_business_domain_website/api/'
        'get_available_business_domains',
    ], type="json", auth='public')
    def get_available_business_domains(self, **post):
        business_domains = request.env['yodoo.business.domain'].search(
            [('knowledge_item_ids', '!=', False)]
        )

        response_data = [
            {
                "id": business_domain.id,
                "name": business_domain.name,
                "code": business_domain.code,
            } for business_domain in business_domains
        ]

        return response_data

    def _get_categories_domain(self, **post):
        domain = super()._get_categories_domain(**post)
        business_domain_id = post.get('business_domain_id')

        if business_domain_id:
            domain.append(
                ['business_domain_id', '=', business_domain_id]
            )

        return domain

    def get_knowledge_item_data(self, item, **post):
        response = super().get_knowledge_item_data(item, **post)

        if item.business_domain_id:
            response['business_domain_id'] = item.business_domain_id.id
        else:
            response['business_domain_id'] = False

        return response

    def _get_search_knowledge_items_domain(self, **post):
        domain = super()._get_search_knowledge_items_domain(**post)

        business_domain_id = post.get('business_domain_id')
        if business_domain_id:
            domain.append(
                ("business_domain_id", "=", business_domain_id)
            )

        return domain
