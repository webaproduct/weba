import functools

from urllib.parse import urlsplit, urlunsplit

import werkzeug

from odoo import http
from odoo.http import request
from odoo.osv import expression


ITEMS_PER_PAGE = 20


def get_redirect():
    full_url = http.request.httprequest.url
    s = urlsplit(full_url)
    url = urlunsplit(['', '', s.path, s.query, s.fragment])
    return werkzeug.urls.url_encode({'redirect': url})


def guard_access(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not http.request.website.is_public_user():
            return func(*args, **kwargs)
        if (request.env.user.company_id.request_wsd_public_ui_visibility ==
                'redirect'):
            url = "/web/login?%s" % get_redirect()
            return http.request.redirect(url)
        return func(*args, **kwargs)
    return wrapper


class WebsiteKnowledge(http.Controller):
    website_id = None

    @http.route(['/knowledge',
                 '/knowledge/item/<model("yodoo.knowledge.item"):item>',
                 '/knowledge/item/<string:code>',
                 '/knowledge/item/<string:code>/<path:any_text>'],
                type='http', auth="public", website=True)
    # @guard_access
    def requests_template(self, item=None, code=None, **kw):
        requested_item = None

        if item:
            requested_item = item
        elif code:
            requested_item = request.env['yodoo.knowledge.item'].sudo().search(
                [('code', '=', code)], limit=1)
        elif kw.get('item_id'):
            requested_item = request.env['yodoo.knowledge.item'].sudo().search(
                [('id', '=', kw.get('item_id'))], limit=1)
        else:
            default_item = request.env['yodoo.knowledge.item'] \
                .search([('is_default', '=', True)], limit=1)
            if default_item:
                requested_item = default_item
            else:
                requested_item = request.env['yodoo.knowledge.item'].search(
                    [], limit=1
                )
        return http.request.render(
            'yodoo_knowledge_website.knowledge_global_template',
            {
                "props": {
                    "website_id": http.request.website.id,
                    "csrf_token": http.request.csrf_token(),
                    "item_code": requested_item.code,
                    "item_id": requested_item.id,
                },
            }
        )

    def _get_filters_domains(self, filters_list, res_model):
        """
        Converts a list of frontend filters into a format suitable for use in
        Odoo ORM domain.

        Parameters:
        - filters_list (list): List of filters, where each filter is
            represented by a dictionary.
            [{"name": "name", "value": ["test1"]}, ...]
        - res_model: resource model_name

        Returns:
        - list: List of tuples representing conditions for Odoo ORM domain.
            [('name', 'in', ["test1", ...]), ...].
        """
        result = []
        for filter_item in filters_list:
            if filter_item.get('name') == 'global_search':
                result.extend([
                    '|',
                    '|',
                    ('id', 'ilike', filter_item.get("value")),
                    ('name', 'ilike', filter_item.get("value")),
                    ('request_text_sample', 'ilike', filter_item.get("value")),
                ])
                continue

            if filter_item.get('name') == 'name':
                result.append((
                    'name', 'ilike', filter_item.get("value")
                ))
                continue

            if filter_item.get('name') == 'create_date_from':
                result.append((
                    'create_date', '>=', filter_item.get('value')
                ))
                continue
            if filter_item.get('name') == 'create_date_to':
                result.append((
                    'create_date', '<=', filter_item.get('value')
                ))
                continue

            additional_filter = self._get_additional_filter(
                filter_item, res_model)
            if additional_filter:
                result.extend(additional_filter)
                continue

            if isinstance(filter_item.get("value"), list):
                if filter_item.get("field_type") == 'many2many':
                    model = http.request.env[res_model].sudo().search(
                        [], limit=1)
                    if hasattr(model, filter_item.get("name")):
                        filter_ids = getattr(
                            model,
                            filter_item.get("name")
                        ).sudo().search([
                            ['name', 'in', filter_item.get("value")]
                        ]).mapped('id')

                        domain = (
                            filter_item.get("name"),
                            "in",
                            filter_ids,
                        )
                        result.append(domain)

                else:
                    domain = (
                        filter_item.get("name"),
                        "in",
                        filter_item.get("value")
                    )
                    result.append(domain)

        return result

    def _get_additional_filter(self, filter_item, res_model) -> list:
        result = []
        if 'tag' in filter_item.get('name'):
            result.append((
                'tag_ids', 'in', filter_item.get("value")
            ))
        return result

    @http.route(route=['/yodoo_knowledge_website/api/get_categories', ],
                type='json', auth='public')
    def get_categories(self, **post):
        self.website_id = post.get('website_id')

        categories_domain = self._get_categories_domain(**post)
        root_categories = request.env[
            'yodoo.knowledge.category'
        ].with_context(**self._get_env_context(**post)).search(
            categories_domain)

        hierarchy = []

        for cat in root_categories:
            category = self.get_category_hierarchy(cat, **post)
            if category:
                hierarchy.append(category)

        return hierarchy

    def _get_categories_domain(self, **post):
        return [
            ('parent_id', '=', False)
        ]

    def _get_env_context(self, **post):
        # created for multilanguage
        return {}

    def get_category_hierarchy(self, category, **post):
        children_categories = http.request.env[
            'yodoo.knowledge.category'
        ].with_context(**self._get_env_context(**post)).search(
            [
                ('parent_id', '=', category.id)
            ]
        )

        children_items = self._get_category_children_knowledge_items(
            category, **post)

        categories_list = []
        for child_category in children_categories:
            child_category_hierarchy = self.get_category_hierarchy(
                child_category, **post)
            if child_category_hierarchy:
                categories_list.append(child_category_hierarchy)

        if not categories_list and not children_items:
            return False

        return {
            'id': category.id,
            'name': category.name,
            'child': {
                'categories': categories_list,
                'items': [
                    {
                        'id': child_item.id,
                        'code': child_item.code,
                        'name': child_item.name,
                        'item_format': child_item.item_format,
                    }
                    for child_item in children_items
                ]
            },
            'parent_id': category.parent_id.id,
        }

    def _get_category_children_knowledge_items(self, category, **post):
        domain = [
            ('category_id', '=', category.id)
        ]
        filters = post.get('filters')
        if filters:
            filters_domain = self._get_filters_domains(
                filters, 'yodoo.knowledge.item')

            domain = expression.AND([
                domain,
                filters_domain
            ])
        return http.request.env['yodoo.knowledge.item'].with_context(
            **self._get_env_context(**post)).search(domain)

    @http.route(['/yodoo_knowledge_website/api/get_knowledge_item', ],
                type="json", auth='public')
    def get_knowledge_item(self, **post):
        item = None

        item_id = post.get('item_id')
        item_code = post.get('item_code')
        if item_id:
            item = http.request.env[
                'yodoo.knowledge.item'
            ].with_context(**self._get_env_context(**post)).search(
                [('id', '=', item_id)])
        elif item_code:
            item = http.request.env[
                'yodoo.knowledge.item'
            ].with_context(**self._get_env_context(**post)).search(
                [('code', '=', item_code)])

        if not item:
            return False

        data = self.get_knowledge_item_data(item, **post)
        return data

    def get_knowledge_item_data(self, item, **post):
        category = item.category_id

        response = {
            'id': item.id,
            'code': item.code,
            'name': item.name,
            'item_format': item.item_format,
            'parent_path': category.parent_path,
        }
        if item.item_format == 'pdf':
            response['pdf_url'] = item.pdf_src_url
        else:
            response['body'] = item.item_body_html

        user = http.request.env['res.users'].sudo().browse(http.request.uid)
        if (
            user.id == 1
            or user.id == item.created_by_id.id
            or user._is_admin()
        ):
            response['internal_url'] = (
                f"/web#model=yodoo.knowledge.item&id={item.id}"
                f"&action=yodoo_knowledge.action_yodoo_knowledge_item"
                f"&view_type=form")
        return response

    @http.route(['/yodoo_knowledge_website/api/search_knowledge_items', ],
                type="json", auth='public', csrf=False)
    def search_knowledge_items(self, **post):
        domain = self._get_search_knowledge_items_domain(**post)

        langs = {
            lang[0]
            for lang in request.env['res.lang'].sudo().get_installed()
        }
        env_with_lang = request.env['yodoo.knowledge.item'].with_context(
            check_translations=True)

        data = []
        found_ids = []

        for lang in langs:
            items = env_with_lang.with_context(lang=lang).search(domain)
            for item in items:
                if item.id in found_ids:
                    continue

                found_ids.append(item.id)
                data.append({
                    'id': item.id,
                    'code': item.code,
                    'name': item.name,
                    'item_format': item.item_format,
                })

        return data

    def _get_search_knowledge_items_domain(self, **post):
        search_text = post.get('search_text')

        domain = [
            '|',
            ('name', 'ilike', search_text),
            ('code', 'ilike', search_text),
            # ('id', 'in', self.env['ir.translation'].search([
            #     ('name', '=', 'your.model,name'),
            #     ('value', 'ilike', 'some_value'),
            #     ('type', '=', 'model')
            # ]).mapped('res_id'))
        ]
        if search_text.isdigit():
            domain.insert(0, '|')
            domain.append(
                ('id', '=', int(search_text))
            )

        return domain

    @http.route(["/yodoo_knowledge_website/api/get_item_types"],
                type='json', auth='public')
    def get_item_types(self, **post):
        self.website_id = post.get('website_id')

        item_types = http.request.env['yodoo.item.type'].search([])

        return self.get_item_type_data(item_types)

    def get_item_type_data(self, item_types):
        result = []
        for item_type in item_types:
            data = {
                "id": item_type.id,
                "name": item_type.display_name
            }
            result.append(data)
        return result

    @http.route(["/yodoo_knowledge_website/api/get_tags"],
                type='json', auth='public')
    def get_tags(self, **post):
        self.website_id = post.get('website_id')

        tags = http.request.env['generic.tag'].search([])

        return self.get_tags_data(tags)

    def get_tags_data(self, tags):
        result = []
        for tag in tags:
            data = {
                "id": tag.id,
                "name": tag.display_name
            }
            result.append(data)
        return result
