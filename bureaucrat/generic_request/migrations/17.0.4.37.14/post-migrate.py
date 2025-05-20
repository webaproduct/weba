from odoo import api, SUPERUSER_ID
from odoo.addons.generic_mixin.tools.migration_utils import (
    ensure_version,
)


@ensure_version('4.37.14')
def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    classifiers = env['request.classifier'].search([])

    for classifier in classifiers:
        classifier.write({
            'request_created_mail_template_id': env.ref(
                'generic_request.mail_template_default_request_create').id,
            'request_assigned_mail_template_id': env.ref(
                'generic_request.mail_template_default_request_assign').id,
            'request_closed_mail_template_id': env.ref(
                'generic_request.mail_template_default_request_closed').id,
            'request_reopened_mail_template_id': env.ref(
                'generic_request.mail_template_default_request_reopened').id,
        })
