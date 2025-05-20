import logging

from odoo import models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class RequestRequest(models.Model):
    _inherit = 'request.request'

    def _notify_get_groups(self, *args, **kwargs):
        """ Use custom url for *button_access* in notification emails
        """
        self.ensure_one()
        groups = super(RequestRequest, self)._notify_get_groups(
            *args, **kwargs)

        if not self.mail_source_id:
            return groups

        # pylint: disable=unused-variable
        for group_name, group_method, group_data in groups:
            if group_name in ('user', 'portal'):
                group_data.setdefault('actions', [])
                available_mail_routes = (
                    self._get_buttons_available_mail_routes())
                group_data['actions'] += available_mail_routes

        return groups

    def _get_buttons_available_mail_routes(self):
        self.ensure_one()
        available_routes = []

        for route in self.stage_id.route_out_ids:
            try:
                route._ensure_can_move(self)
                if route.is_available_in_email:
                    available_routes.append({
                        'url': route.get_mail_url_for(self),
                        'title': route.name or route.display_name,
                    })
            except AccessError:
                _logger.info('Cannot move %s by route %s, skipping...',
                             self.display_name, route.display_name)

        return available_routes
