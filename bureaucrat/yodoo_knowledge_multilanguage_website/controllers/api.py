from odoo import http
from odoo.http import request

from odoo.addons.yodoo_knowledge_website.controllers.api import (
    WebsiteKnowledge)


class WebsiteKnowledgeMultilanugage(WebsiteKnowledge):
    def _get_env_context(self, **post):
        context = super()._get_env_context(**post)
        language_id = post.get('language_id')
        if language_id:
            lang = request.env['res.lang'].sudo().browse(language_id)
            installed_lang_codes = {
                lang[0]
                for lang in request.env['res.lang'].sudo().get_installed()
            }

            if (
                lang
                and lang.code in installed_lang_codes
            ):
                context['lang'] = lang.code
        return context

    # def _get_category_children_knowledge_items(self, category, **post):
    #     knowledge_items = super()._get_category_children_knowledge_items(
    #         category, **post)
    #     language_id = post.get('language_id')
    #     if not language_id:
    #         return knowledge_items
    #
    #     knowledge_items_by_lang = []
    #     for item in knowledge_items:
    #         translated_item = item._get_history_item_by_lang(language_id)
    #         if translated_item:
    #             knowledge_items_by_lang.append(item)
    #     return knowledge_items_by_lang

    @http.route([
        '/yodoo_knowledge_multilanguage_website/api/get_available_languages',
    ], type="json", auth='public')
    def get_available_languages(self, **post):
        languages = request.env['res.lang'].search(
            [('active', '=', True)]
        )

        response_data = [
            {
                "id": language.id,
                "name": language.name,
                "code": language.code,
            } for language in languages
        ]

        return response_data

    def get_knowledge_item_data(self, item, **post):
        data = super().get_knowledge_item_data(item, **post)

        language_id = post.get('language_id')
        if language_id:
            translated_item = item._get_history_item_by_lang(language_id)
            if translated_item:
                if data.get('item_format') == 'pdf':
                    data.update({
                        'pdf_url': translated_item.pdf_src_url
                    })
                else:
                    data.update({
                        'body': translated_item.item_body_html,
                    })

        return data
