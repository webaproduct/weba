import re
import base64
import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _request_mail_action__parse_subject(self, message_dict):
        """ Parse mail message and try to find request and route
            from subject
        """
        # flake8: noqa: E501
        m = re.match(
            r"^.*\[([a-zA-Z0-9=\+]+)\]$",
            message_dict.get('subject', ''))
        if not m:
            return False

        subject_code = base64.b64decode(m.group(1)).decode('utf-8')
        m = re.match(
            r"^request-(?P<request_id>[0-9]+)-route-(?P<route_id>[0-9]+)(?:-req_user_id-(?P<req_user_id>[0-9]+))?",
            subject_code)
        request_id = int(m.group("request_id"))
        route_id = int(m.group("route_id"))
        email = message_dict.get('from')
        req_partner_id = self._mail_action_find_partner_from_email(email)
        if req_partner_id and len(req_partner_id) == 1:
            req_user_id = req_partner_id[0].user_ids.id
            if not req_user_id:
                _logger.warning(
                    "No user found for partner %s", req_partner_id[0].name)
                return False
        else:
            return False

        if not m:
            return False

        return request_id, route_id, req_user_id

    def _mail_action_find_partner_from_email(self, email):
        partner = self._mail_find_partner_from_emails(
            [email], force_create=False)
        return partner

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None,
                      custom_values=None):
        _logger.warning(
            "XXX: Processing mail with subject: %s",
            message_dict.get('subject', ''))
        res = self._request_mail_action__parse_subject(message_dict)
        if not res:
            return super().message_route(
                message, message_dict, model=model, thread_id=thread_id,
                custom_values=custom_values)

        request_id, route_id, user_id = res

        request = self.env['request.request'].browse(request_id)
        route = self.env['request.stage.route'].browse(route_id)
        user = self.env['res.users'].browse(user_id)

        # Perform actions in the context of the specified user
        request = self._apply_user_context(request, user)
        route = self._apply_user_context(route, user)
        try:
            self._process_mail_action(request, route, message_dict)
        except Exception as e:
            _logger.error(
                "Error occurred while process mail action for request %s "
                "and route %s: %s", request_id, route_id, str(e),
            )
            return []

        # No further processing of message needed, thus just returning empty
        # list
        return []

    @api.model
    def _apply_user_context(self, record, user):
        """Switch the record's environment to the specified user."""
        return record.with_user(user)

    @api.model
    def _process_mail_action(self, request, route, message_dict):
        """Handle the action provided by email"""
        _logger.info("Moving request %s by route %s as requested by email.",
                     request.name, route.display_name)
        request.stage_id = route.stage_to_id
        request.response_text = message_dict.get('body')
