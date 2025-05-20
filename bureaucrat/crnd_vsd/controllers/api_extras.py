import logging

from odoo import http
from markupsafe import Markup

_logger = logging.getLogger(__name__)


class WebsiteExtraController(http.Controller):
    @http.route(["/api/get_allowed_table_columns"], type='json', auth='public')
    def get_allowed_table_columns(self, **post):
        allowed_fields = []

        # website_id = post.get('website_id')
        # website = http.request.env['website'].sudo().search([
        #     ("id", "=", website_id),
        # ], limit=1)
        for field_name, res_param in (
                http.request.env['res.config.settings']._fields.items()):
            if 'request_list_column_' in field_name:
                if http.request.env['ir.config_parameter'].sudo(
                ).get_param(res_param.config_parameter):
                    allowed_fields.append(field_name.replace(
                        'request_list_column_', ''))
        return allowed_fields

    @http.route(["/api/get_allowed_read_blocks"], type='json', auth='public')
    def get_allowed_read_blocks(self, **post):
        allowed_fields = []

        request_id = post.get('request_id')
        if not request_id:
            return allowed_fields
        req = http.request.env['request.request'].sudo().browse(request_id)
        classifier = req.classifier_id

        for field_name in classifier._fields.keys():
            if 'read_show_' in field_name:
                if getattr(classifier, field_name):
                    allowed_fields.append(field_name.replace(
                        'read_show_', ''))

        return allowed_fields

    @http.route(["/api/add_comment_to_request"], type='json', auth='public')
    def add_comment_to_request(self, **post):
        message_text = post.get('message_text')
        attachment_ids = post.get('attachment_ids', [])
        if not message_text and not attachment_ids:
            return {
                "status": 404,
                "message": "Empty message"
            }
        request_id = post.get('request_id')
        request = http.request.env['request.request'].sudo().search([
            ("id", "=", request_id),
        ])
        if not request:
            return {
                "status": 404,
                "message": "Wrong request_id"
            }

        try:
            _logger.info(
                "API: Adding comment to request ID %s via API", request_id)

            message = request.sudo().message_post(
                body=Markup(message_text or ''),  # nosec B704
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                attachment_ids=attachment_ids,
                author_id=http.request.env.user.partner_id.id
            )

            request._process_attachments_for_post(
                [], attachment_ids,
                {'res_id': request.id, 'model': "request.request"}
            )

            return {
                "status": 200,
                "comment_id": message.id
            }
        except Exception as e:
            _logger.exception(
                "Error adding comment to request #%s: %s", request_id, e)
            return {
                "status": 500,
                "message": "Server error: Could not post comment"
            }

    @http.route(["/api/get_create_fields_visibility"], type='json',
                auth='public')
    def get_create_fields_visibility(self, **post):
        visible_fields = []

        service_id = post.get('service_id')
        category_id = post.get('category_id')
        type_id = post.get('type_id')

        classifier = http.request.env['request.classifier'].sudo().search([
            ['service_id', '=', service_id],
            ['category_id', '=', category_id],
            ['type_id', '=', type_id],
        ])

        for field_name in classifier._fields.keys():
            if 'create_show_' in field_name:
                if getattr(classifier, field_name):
                    visible_fields.append(field_name.replace(
                        'create_show_', ''))

        return visible_fields

    @http.route(["/api/get_available_followers"], type='json',
                auth='public')
    def get_available_followers(self, **post):
        request_id = post.get('request_id')

        request = http.request.env['request.request'].search([
            ('id', '=', request_id),
        ])

        partners = http.request.env['res.partner'].search([
            ('id', 'not in', request.sec_view_access_partner_ids.mapped('id')),
        ])

        return [{
            "id": partner.id,
            "name": partner.name,
            "display_name": partner.complete_name,
            "email": partner.email_normalized
        } for partner in partners]

    @http.route(["/api/add_follower_to_request"], type='json',
                auth='public')
    def add_follower_to_request(self, **post):
        request_id = post.get('request_id')
        follower_id = post.get('follower_id')

        request = http.request.env['request.request'].search([
            ('id', '=', request_id),
        ])

        request.message_subscribe(partner_ids=[follower_id])
        return True

    @http.route(["/api/remove_follower_for_request"], type='json',
                auth='public')
    def remove_follower_for_request(self, **post):
        request_id = post.get('request_id')
        follower_id = post.get('follower_id')

        request = http.request.env['request.request'].search([
            ('id', '=', request_id),
        ])

        request.message_unsubscribe(partner_ids=[follower_id])

        return True
