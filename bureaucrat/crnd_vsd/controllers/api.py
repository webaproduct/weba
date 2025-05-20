# pylint: disable=too-many-lines
import datetime
import functools

from urllib.parse import urlsplit, urlunsplit
from defusedxml.ElementTree import fromstring

import werkzeug

from odoo import _
from odoo import http
from odoo.http import request
from odoo.osv import expression

from odoo.loglevels import ustr

from odoo.exceptions import AccessError, ValidationError
from .controller_mixin import WSDControllerMixin
from .utils import CRNDVsdCreateDataListError

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


class WebsiteRequest(WSDControllerMixin, http.Controller):
    GROUP_USER_ADVANCED = (
        'crnd_wsd.group_service_desk_website_user_advanced'
    )
    website_id = None

    def _get_datetime_field_value(self, datetime_field):
        if not datetime_field:
            return False

        use_time = http.request.website.request_use_time_in_datetime_on_website
        datetime_format = http.request.lang.date_format

        if use_time and isinstance(datetime_field, datetime.datetime):
            time_format = http.request.lang.time_format.replace(':%S', '')
            datetime_format += f" {time_format}"
        return datetime_field.strftime(datetime_format)

    @http.route(['/requests',
                 '/requests/<string:req_status>',
                 '/requests/<string:req_status>/page/<int:page>'],
                type='http', auth="public", website=True)
    @guard_access
    def requests_template(self):
        data = {
            "props": {
                "use_service_groups":
                    http.request.website.use_service_groups
                    and http.request.env.user.has_group(
                        'generic_request.group_request_use_services'),
                "use_service": http.request.env.user.has_group(
                    'generic_request.group_request_use_services'),
                "use_quick_filters":
                    http.request.website.request_quick_filters_on_website,
                "website_id": http.request.website.id,
                "csrf_token": http.request.csrf_token(),
                "date_format": http.request.lang.date_format,
                "time_format": http.request.lang.time_format,
            },
            "session_info": http.request.env['ir.http'].session_info(),
            "contained": http.request.website.request_contained_on_website,
        }
        return http.request.render('crnd_vsd.requests_global_template', data)

    def _request_new_get_public_classifiers_base_domain(self):
        if http.request.env.user.has_group(self.GROUP_USER_ADVANCED):
            domain = []
        else:
            domain = [('website_published', '=', True)]

        return expression.AND([
            domain,
            ['|',
             ('website_ids', '=', False),
             ('website_ids', 'in', self.website_id)]
        ])

    def _get_classifiers(
            self,
            service_id=None,
            category_id=None,
            filter_by_service=False,
            filter_by_category=False
    ):
        classifiers_domain = (
            self._request_new_get_public_classifiers_base_domain())

        if filter_by_service:
            service = self._id_to_record('generic.service', service_id)
            if service:
                classifiers_domain = expression.AND([
                    classifiers_domain,
                    [('service_id', '=', service.id)]])
            else:
                classifiers_domain = expression.AND([
                    classifiers_domain,
                    [('service_id', '=', False)]])

        if filter_by_category:
            if category_id:
                classifiers_domain = expression.AND([
                    classifiers_domain,
                    [('category_id', '=', category_id)],
                ])
            else:
                classifiers_domain = expression.AND([
                    classifiers_domain,
                    [('category_id', '=', False)],
                ])

        return request.env['request.classifier'].search(
            classifiers_domain)

    @staticmethod
    def create_image_url(model, rec_id, field='image_1920'):
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        return (f"{base_url}/web/image?model={model}"
                f"&id={rec_id}&field={field}")

    ########################################################
    #                    SERVICE GROUP                     #
    ########################################################
    @http.route(route=['/api/get_services_group', ],
                type='json', auth='public', website=True)
    def get_services_group(self, **post):
        self.website_id = post.get('website_id')
        public_services = self._request_new_get_public_services(**post)

        # public_services = public_services.filtered(
        #     lambda r: self._request_new_get_public_categs(
        #         service_id=r.id
        #     ) or self._check_if_types_exist(service_id=r.id)
        # )

        service_groups = public_services.mapped('service_group_id')

        return self.get_service_group_data(service_groups)

    def get_service_group_data(self, service_groups):
        result = []
        for service_group in service_groups:
            data = {
                "id": service_group.id,
                "name": service_group.display_name,
            }
            if service_group.image_128:
                data['image'] = self.create_image_url(
                    service_group._name,
                    service_group.id,
                    field='image_128'
                )
            result.append(data)
        return result

    ########################################################
    #                       SERVICE                        #
    ########################################################
    @http.route(route=['/api/get_services', ],
                type='json', auth='public', website=True)
    def get_services(self, **post):
        self.website_id = post.get('website_id')
        public_services = self._request_new_get_public_services(**post)

        # public_services = public_services.filtered(
        #     lambda r: self._request_new_get_public_categs(
        #         service_id=r.id
        #     ) or self._check_if_types_exist(service_id=r.id)
        # )
        service_group_id = post.get('service_group_id')
        if service_group_id:
            public_services = public_services.filtered(
                lambda r: r.service_group_id.id == int(service_group_id))

        return self.get_service_data(public_services)

    def get_service_data(self, services):
        result = []
        for service in services:
            data = {
                "id": service.id,
                "name": service.display_name,
            }
            if service.image_128:
                data['image'] = self.create_image_url(
                    service._name,
                    service.id,
                    field='image_128'
                )
            result.append(data)
        return result

    def _request_new_get_public_services(self, **post):
        domain = self._request_new_get_public_services_domain(**post)
        result = request.env['generic.service'].search(domain)
        return result

    def _request_new_get_public_services_domain(self, **post):
        classifiers = self._get_classifiers()
        return [('id', 'in', classifiers.mapped('service_id').ids)]

    ########################################################
    #                       CATEGORY                       #
    ########################################################
    @http.route(route=['/api/get_categories', ],
                type='json', auth='public', website=True)
    def get_categories(self, **post):
        self.website_id = post.get('website_id')
        service_id = post.get('service_id')
        filter_by_service = post.get('filter_by_service', True)

        public_categories = self._request_new_get_public_categs(
            service_id=service_id,
            filter_by_service=filter_by_service,
        )

        return self.get_category_data(public_categories)

    def get_category_data(self, categories):
        result = []
        for cat in categories:
            # TODO: add icon for categ
            data = {
                "id": cat.id,
                "name": cat.display_name
            }
            result.append(data)
        return result

    def _request_new_get_public_categs(
        self,
        service_id=None,
        filter_by_service=True,
    ):
        domain = self._request_new_get_public_categs_domain(
            service_id=service_id,
            filter_by_service=filter_by_service,
        )
        categs = http.request.env['request.category'].search(domain)
        # .filtered(
        #     lambda r: self._check_if_types_exist(
        #         category_id=r.id,
        #         service_id=service_id
        #     )
        # )
        return categs

    def _request_new_get_public_categs_domain(
        self,
        service_id=None,
        filter_by_service=True,
    ):
        classifiers = self._get_classifiers(
            service_id=service_id,
            filter_by_service=filter_by_service,
        )
        domain = [('id', 'in', classifiers.mapped('category_id').ids)]
        return domain

    ########################################################
    #                         TYPE                         #
    ########################################################
    @http.route(["/api/get_types"], type='json',
                auth='public', website=True)
    def get_types(self, **post):
        self.website_id = post.get('website_id')
        category_id = post.get('category_id')
        service_id = post.get('service_id')
        filter_by_service = post.get('filter_by_service', True)
        filter_by_category = post.get('filter_by_category', True)

        req_category = self._id_to_record('request.category', category_id)
        req_service = self._id_to_record('generic.service', service_id)

        public_types = self._request_new_get_public_types(
            category_id=req_category.id,
            service_id=req_service.id,
            filter_by_service=filter_by_service,
            filter_by_category=filter_by_category,
        )

        return self.get_type_data(public_types)

    def get_type_data(self, types):
        result = []
        for type_obj in types:
            # TODO: add icon for categ
            data = {
                "id": type_obj.id,
                "name": type_obj.display_name
            }
            result.append(data)
        return result

    def _request_new_get_public_types_domain(
        self,
        service_id=None,
        category_id=None,
        filter_by_service=True,
        filter_by_category=True
    ):
        classifiers = self._get_classifiers(
            service_id=service_id,
            category_id=category_id,
            filter_by_service=filter_by_service,
            filter_by_category=filter_by_category
        )
        domain = [('id', 'in', classifiers.mapped('type_id').ids)]
        return domain

    def _request_new_get_public_types(
        self,
        category_id=None,
        service_id=None,
        filter_by_service=True,
        filter_by_category=True,
    ):
        domain = self._request_new_get_public_types_domain(
            category_id=category_id,
            service_id=service_id,
            filter_by_service=filter_by_service,
            filter_by_category=filter_by_category,
        )

        return http.request.env['request.type'].search(domain)

    # def _check_if_types_exist(self, category_id=None, service_id=None):
    #     domain = self._request_new_get_public_types_domain(
    #         service_id=service_id,
    #         category_id=category_id
    #     )
    #
    #     return http.request.env['request.type'].search_count(domain)

    ########################################################
    #                         STAGE                        #
    ########################################################
    @http.route(["/api/get_stages"], type='json',
                auth='public', website=True)
    def get_stages(self, **post):
        self.website_id = post.get('website_id')

        stages = http.request.env['request.stages'].search(
            ['request_ids', '=', True]
        )

        return self.get_stages_data(stages)

    @staticmethod
    def get_stages_data(stages):
        result = []
        for stage_obj in stages:
            data = {
                "id": stage_obj.id,
                "name": stage_obj.display_name,
                "bg_color": stage_obj.bg_color
            }
            result.append(data)
        return result

    ########################################################
    #                       REQUEST                        #
    ########################################################
    @http.route(["/api/get_requests_template"], type='json',
                auth='public')
    def get_requests_template(self, **post):
        self.website_id = post.get('website_id')

        service_id = post.get('service_id')
        type_id = post.get('type_id')
        category_id = post.get('category_id')

        req_service = self._id_to_record('generic.service', service_id)
        req_type = self._id_to_record('request.type', type_id)
        req_category = self._id_to_record('request.category', category_id)

        template_data = self._get_template_data(
            req_service=req_service,
            req_category=req_category,
            req_type=req_type,
            **post
        )

        template_name = self._get_template_name()

        template = request.env["ir.ui.view"]._render_template(
            template_name,
            template_data
        )
        return {
            "template": template,
        }

    def _get_template_data(self, req_service, req_category, req_type, **post):
        classifier = http.request.env['request.classifier'].sudo().search([
            ['service_id', '=', req_service.id],
            ['category_id', '=', req_category.id],
            ['type_id', '=', req_type.id],
        ])

        request_default_title = ''
        request_default_text = ''

        if classifier.default_priority_request_title:
            request_default_title = classifier.default_priority_request_title

        if (classifier.default_priority_request_text
                and classifier.default_priority_request_text != '<p><br></p>'):
            request_default_text = classifier.default_priority_request_text
        elif (classifier.type_id.default_request_text
                and classifier.type_id.default_request_text != '<p><br></p>'):
            request_default_text = classifier.type_id.default_request_text

        return {
            'classifier': classifier,
            'request_default_title': request_default_title,
            'request_default_text': request_default_text,
        }

    def _get_template_name(self):
        if request.env['ir.config_parameter'].sudo(
        ).get_param('crnd_vsd.request_use_custom_template'):
            return 'crnd_vsd.requests_create_global_custom_template'
        return 'crnd_vsd.requests_create_global_template'

    @http.route(["/api/create_request"], type='json',
                auth='public')
    def create_request(self, **post):
        self.website_id = post.get('website_id')

        try:
            req_data = self._request_new_prepare_data(**post)
        except CRNDVsdCreateDataListError as e:
            # TODO: add status for Response class
            # return HTTPRequest(http.request).make_json_response(json.dumps({
            #     'required_fields': e.field_name_list
            # }), status=422, content_type='application/json')
            return {
                "status_code": 422,
                "required_fields": e.field_name_list,
            }

        Request = http.request.env['request.request']

        with http.request.env.cr.savepoint():
            req = Request.create(req_data)
            req._request_bind_attachments()
            req_id = req.id

            self._request_post_create_data(req, **post)

        return {
            "req_id": req_id,
        }

    def _request_new_prepare_data(self, **post):
        service_id = post.get('service', {}).get('id')
        type_id = post.get('type', {}).get('id')
        category_id = post.get('category', {}).get('id')

        req_service = self._id_to_record('generic.service', service_id)
        req_type = self._id_to_record('request.type', type_id)
        req_category = self._id_to_record('request.category', category_id)

        req_data = post.get('requestData')
        req_text = post.get('requestData', {}).get('request_text')

        error_fields = self._validate_data_for_create(
            req_service,
            req_type,
            req_category,
            **req_data
        )
        if error_fields:
            raise CRNDVsdCreateDataListError('Required fields', error_fields)

        res = {
            'service_id': req_service and req_service.id,
            'category_id': req_category and req_category.id,
            'type_id': req_type.id,
            'request_text': req_text,
            'title': req_data.get('title'),
            'website_id': self.website_id,
        }
        service = self._id_to_record(
            'generic.service',
            req_data.get('service', {}).get('id')
        )
        if service:
            res['service_id'] = service.id
        if post.get('parent_id'):
            res['parent_id'] = post.get('parent_id')

        return res

    def _validate_data_for_create(self, req_service, req_type,
                                  req_category, **req_data):
        error_fields = []  # now for required_fields

        template_data = self._get_template_data(
            req_service=req_service,
            req_category=req_category,
            req_type=req_type,
            **req_data
        )
        template = request.env["ir.ui.view"]._render_template(
            self._get_template_name(),
            template_data
        )
        root = fromstring(template)
        elements = root.findall('.//{}'.format('field'))

        for field_item in elements:
            if ("required" in field_item.attrib and
                    field_item.attrib.get("required") in [
                        'true', 'True', True]):
                if not req_data.get(field_item.attrib.get("name")):
                    error_fields.append(field_item.attrib.get("name"))

        return error_fields

    def _request_post_create_data(self, req, **post):
        return

    ########################################################
    #                    REQUEST GETTER                    #
    ########################################################
    @http.route(route=['/api/get_requests', ], type='json',
                auth='public', website=True)
    def get_requests(self, **post):
        # pylint: disable=too-many-locals
        self.website_id = post.get('website_id')

        req_status = post.get('req_status') or 'my'
        page = post.get('page') or 1
        search = post.get('search') or ""
        filter_list = post.get('filter_list')
        sorting = self._get_sorting_method(post.get('sorting'))

        if req_status not in ('my', 'open', 'closed', 'all', 'for_me'):
            return "ERROR with req_status"

        Request = http.request.env['request.request']

        domains = self._requests_get_request_domains(search, **post)

        # pagination settings
        limit = http.request.env['website'].sudo().browse(
            self.website_id).request_pagination_on_website
        offset = limit * (page - 1)

        domain = domains[req_status]

        if filter_list:
            filters_list_domain = self._get_filters_domains(
                filter_list, 'request.request')

            domain = expression.AND([
                domain,
                filters_list_domain
            ])

        reqs_count = Request.search_count(domain)

        # for Next n Prev button in ReadView
        request.session['crnd_requests_history'] = Request.search(
            domain).ids

        reqs = Request.search(
            domain,
            limit=limit,
            offset=offset,
            order=sorting
        )
        values = {
            "reqs": self.get_requests_data(reqs),
            "pages_count": self.paginate(reqs_count, limit),
            "items_count": reqs_count,
        }
        return values

    def _get_sorting_method(self, value):
        return value

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
            if (filter_item.get('name') == 'global_search'
                    and filter_item.get("value")):
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
        return []

    @staticmethod
    def paginate(list_length, items_per_page):
        pages = list_length // items_per_page
        remainder = list_length % items_per_page
        if remainder > 0:
            pages += 1
        return pages

    def get_requests_data(self, reqs):
        result = []
        for req in reqs:
            data = {
                "id": req.id,
                "title": req.title,
                "name": req.name,
                "creation_date": self._get_datetime_field_value(
                    req.create_date),
                "created_by": {
                    "id": req.created_by_id.id,
                    "name": req.created_by_id.name,
                    "image_url": self.create_image_url(req.created_by_id._name,
                                                       req.created_by_id.id)
                },
                "service": {
                    "id": req.service_id.id,
                    "name": req.service_id.display_name
                } if req.service_id else False,
                "category": {
                    "id": req.category_id.id,
                    "name": req.category_id.display_name
                } if req.category_id else False,
                "type": {
                    "id": req.type_id.id,
                    "name": req.type_id.sudo().display_name
                } if req.type_id else False,
                "request_text_sample": req.request_text_sample[:30] + ' ...'
                if len(req.request_text_sample) > 30
                else req.request_text_sample,
                "assigned_to": {
                    "id": req.user_id.id,
                    "name": req.user_id.name,
                    "image_url": self.create_image_url(req.user_id._name,
                                                       req.user_id.id)
                },
                "message_attachment_count":
                    req.sudo().message_attachment_count,
                "comments": [
                    {
                        "id": comment.id,
                        "text": comment.preview,
                    } for comment in req.message_ids if
                    comment.message_type == 'comment'
                ],
                "stage": {
                    "id": req.stage_id.id,
                    "name": req.stage_id.name,
                    "bg_color": req.stage_bg_color,
                }
            }
            result.append(data)
        return result

    @http.route(route=['/api/get_requests/<int:request_id>', ],
                type='json', auth='public', website=True)
    def get_request(self, request_id, **post):
        self.website_id = post.get('website_id')

        req = http.request.env['request.request'].search(
            [("id", "=", request_id)]
        )
        if not req:
            return {
                "error": "Not found"
            }

        request_data = self.get_single_request_data(req.sudo())
        return {
            "data": request_data,
        }

    def _request_get_available_routes(self, req, **post):
        Route = http.request.env['request.stage.route']
        result = []

        website = http.request.env['website'].sudo().browse(
            self.website_id)
        if request.env.user.id == website._get_cached('user_id'):
            return result

        user = http.request.env.user
        group_ids = user.sudo().groups_id.ids
        action_routes = Route.search(expression.AND([
            [('request_type_id', '=', req.sudo().type_id.id)],
            [('stage_from_id', '=', req.sudo().stage_id.id)],
            [('website_published', '=', True)],
            expression.OR([
                [('allowed_user_ids', '=', False)],
                [('allowed_user_ids', '=', user.id)],
            ]),
            expression.OR([
                [('allowed_group_ids', '=', False)],
                [('allowed_group_ids', 'in', group_ids)],
            ]),
        ]))

        for route in action_routes:
            try:
                route._ensure_can_move(req)
            except AccessError:  # pylint: disable=except-pass
                pass
            except ValidationError:  # pylint: disable=except-pass
                pass
            else:
                result.append({
                    "id": route.id,
                    "name": route.name,
                    "button_style": route.button_style,
                    "stage_to_id": route.stage_to_id.id,
                })
        return result

    @http.route(route=['/api/update_request/<int:request_id>', ],
                type='json', auth='public', website=True)
    def update_request(self, request_id, **post):
        self.website_id = post.get('website_id')

        req = http.request.env['request.request'].search(
            [("id", "=", request_id)]
        )
        if not req:
            return {
                "error": "Not found"
            }

        request_text = post.get('request_text')
        title = post.get('title')
        stage_id = post.get('stage_id')
        try:
            if request_text:
                req.request_text = request_text
            if title:
                req.title = title
            if stage_id:
                req.stage_id = stage_id
        except Exception as exc:
            return {
                'error': _("Access denied"),
                'debug': ustr(exc),
            }

        request_data = self.get_single_request_data(req.sudo())
        return {
            "data": request_data,
        }

    def get_single_request_data(self, req):
        data = {
            "id": req.id,
            "name": req.display_name,
            "title": req.title,
            "can_edit": not req.closed and req.can_change_request_text,
            "creation_date": self._get_datetime_field_value(req.create_date),
            "created_by": {
                "id": req.created_by_id.id,
                "name": req.created_by_id.name,
                "image_url": self.create_image_url(req.created_by_id._name,
                                                   req.created_by_id.id)
            },
            "request_text": req.request_text,
            "assigned_to": {
                "id": req.user_id.id,
                "name": req.user_id.name,
                "image_url": self.create_image_url(req.user_id._name,
                                                   req.user_id.id)
            } if req.user_id else False,
            "updated_by": {
                "id": req.write_uid.id,
                "name": req.write_uid.name,
                "image_url": self.create_image_url(req.write_uid._name,
                                                   req.write_uid.id)
            } if req.write_uid else False,
            "closed_by": {
                "id": req.closed_by_id.id,
                "name": req.closed_by_id.name,
                "image_url": self.create_image_url(req.closed_by_id._name,
                                                   req.closed_by_id.id)
            } if req.closed_by_id else False,
            "responsible": {
                "id": req.responsible_id.id,
                "name": req.responsible_id.name,
                "image_url": self.create_image_url(req.responsible_id._name,
                                                   req.responsible_id.id)
            } if req.responsible_id else False,
            "attachments": {
                "count": len(req.sudo().attachment_ids),
                "ids": [
                    {
                        "id": attachment.id,
                        "name": attachment.name,
                        "url": self._get_attachment_url(attachment),
                    } for attachment in req.sudo().attachment_ids
                ]
            },
            "stage": {
                "id": req.stage_id.id,
                "name": req.stage_id.name,
                "bg_color": req.stage_bg_color,
            },
            "service": {
                "id": req.service_id.id,
                "name": req.service_id.display_name
            } if req.service_id else False,
            "category": {
                "id": req.category_id.id,
                "name": req.category_id.display_name
            } if req.category_id else False,
            "type": {
                "id": req.type_id.id,
                "name": req.type_id.sudo().display_name
            } if req.type_id else False,
            "priority": req.priority,
            "comments": [
                {
                    "id": comment.id,
                    "text": comment.body,
                    "user_name": comment.author_id.name,
                    "user_image_url": self.create_image_url(
                        comment.author_id._name, comment.author_id.id),
                    "creation_date": self._get_datetime_field_value(
                        comment.create_date),
                    "attachments": [{
                        "id": attachment.id,
                        "url": self._get_attachment_url(attachment),
                        "type": attachment.index_content,
                        "name": attachment.display_name,
                        "access_token": self._get_attachment_token(attachment),
                    } for attachment in comment.sudo().attachment_ids]
                } for comment in req.message_ids
                if comment.message_type in ('comment', 'email')
            ],

            "parent_request": {
                "id": req.parent_id.id,
                "name": req.parent_id.display_name,
                "request_text_sample": req.parent_id.request_text_sample,
                "stage": {
                    "id": req.parent_id.stage_id.id,
                    "name": req.parent_id.stage_id.name,
                    "bg_color": req.parent_id.stage_bg_color,
                },
                "service": {
                    "id": req.parent_id.service_id.id,
                    "name": req.parent_id.service_id.display_name
                } if req.parent_id.service_id else False,
                "category": {
                    "id": req.parent_id.category_id.id,
                    "name": req.parent_id.category_id.display_name
                } if req.parent_id.category_id else False,
                "type": {
                    "id": req.parent_id.type_id.id,
                    "name": req.parent_id.type_id.sudo().display_name
                } if req.parent_id.type_id else False,
                "creation_date": self._get_datetime_field_value(
                    req.parent_id.create_date),
            } if req.parent_id else False,

            "subrequests": [
                {
                    "id": subreq.id,
                    "name": subreq.display_name,
                    "request_text_sample": subreq.request_text_sample,
                    "stage": {
                        "id": subreq.stage_id.id,
                        "name": subreq.stage_id.name,
                        "bg_color": subreq.stage_bg_color,
                    },
                    "service": {
                        "id": subreq.service_id.id,
                        "name": subreq.service_id.display_name
                    } if subreq.service_id else False,
                    "category": {
                        "id": subreq.category_id.id,
                        "name": subreq.category_id.display_name
                    } if subreq.category_id else False,
                    "type": {
                        "id": subreq.type_id.id,
                        "name": subreq.type_id.sudo().display_name
                    } if subreq.type_id else False,
                    "creation_date": self._get_datetime_field_value(
                        subreq.create_date),
                } for subreq in req.child_ids
            ],

            "routes": self._request_get_available_routes(req),
        }

        if (
            http.request.env.user.has_group(
                "generic_request.group_request_user")
            or http.request.env.user.has_group(
                "generic_request.group_request_manager")
        ) and req.with_user(http.request.env.user).check_access_rights(
            "read", raise_exception=False
        ):
            data["internal_url"] = (
                f"/web#model=request.request&id={req.id}"
                f"&action=generic_request.action_request_window"
                f"&view_type=form"
            )

            data["followers"] = [{
                "id": follower.id,
                "display_name": follower.complete_name,
                "email": follower.email_normalized
            } for follower in req.sec_view_access_partner_ids]

        history = request.session.get('crnd_requests_history', [])
        try:
            current_req_index = history.index(req.id)
        except ValueError:
            return data
        data['current_req_index'] = current_req_index + 1
        data['history_length'] = len(history)
        data['next_record_id'] = history[current_req_index + 1] \
            if current_req_index < len(history)-1 else None
        data['prev_record_id'] = history[current_req_index - 1] \
            if current_req_index > 0 else None

        return data

    def _get_attachment_token(self, attachment):
        attachment.generate_access_token()
        return attachment.access_token

    def _get_attachment_url(self, attachment):
        return f'/web/content/{attachment.id}?unique={attachment.checksum}'

    def _requests_get_request_domains(self, search, **post):
        domain = self._requests_get_request_domain_base(search, **post)

        return {
            'all': domain,
            'open': domain + [('closed', '=', False)],
            'closed': domain + [('closed', '=', True)],
            'my': domain + [
                ('closed', '=', False),
                '|',
                # '|',
                # ('user_id', '=', http.request.env.user.id),
                ('created_by_id', '=', http.request.env.user.id),
                ('author_id', '=', http.request.env.user.partner_id.id),
            ],
            'for_me': domain + [
                ('closed', '=', False),
                ('user_id', '=', http.request.env.user.id),
            ]
        }

    def _requests_get_request_domain_base(self, search, kind_id=None,
                                          parent_id=None, **post):
        domain = [
            '|',
            ('website_id', '=', False),
            ('website_id', '=', post.get('website_id')),
        ]
        if search:
            domain += self._requests_get_request_search_domain_base(search)

        kind = self._id_to_record('request.kind', kind_id, no_raise=True)
        if kind:
            domain = expression.AND([
                domain,
                [('kind_id', '=', kind.id)],
            ])

        parent = self._id_to_record(
            'request.request', parent_id, no_raise=True)
        if parent:
            domain += [('parent_id', '=', parent.id)]

        return domain
