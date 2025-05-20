import base64
import werkzeug.urls

from odoo import models, fields


class RequestStageRoute(models.Model):
    _inherit = 'request.stage.route'

    is_available_in_email = fields.Boolean(
        default=False, index=True,
        help="If set, then it will be possible to trigger this route "
             "from email.")

    def get_mail_subject_code_for(self, request):
        subject_code = "request-%s-route-%s-req_user_id-%s" % (
            request.id,
            self.id,
            request.user_id.id)

        return "%(name)s - [%(code)s]" % {
            'name': self.name or self.display_name,
            'code': base64.b64encode(
                subject_code.encode('utf-8')
            ).decode('utf-8'),
        }

    def get_mail_url_for(self, request):
        self.ensure_one()
        if not request.mail_source_id:
            # Currently, this feature works only for requests with
            # related mail sources.
            return None

        params = werkzeug.urls.url_encode({
            'subject': self.get_mail_subject_code_for(request),
            'body': self.name or self.display_name,
        })
        return "mailto:%(email)s?%(params)s" % {
            'email': "%s@%s" % (
                request.mail_source_id.alias_name,
                request.mail_source_id.alias_domain,
            ),
            'params': params
        }
