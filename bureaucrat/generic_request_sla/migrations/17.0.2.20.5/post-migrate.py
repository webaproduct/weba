from odoo import api, SUPERUSER_ID
from odoo.addons.generic_mixin.tools.migration_utils import (
    ensure_version,
)


@ensure_version('2.20.5')
def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    classifiers = env['request.classifier'].search([])

    warn_template = env.ref(
        'generic_request_sla.mail_template_default_request_sla_warning')
    fail_template = env.ref(
        'generic_request_sla.mail_template_default_request_sla_failed')

    for classifier in classifiers:
        classifier.write({
            'request_sla_warning_mail_template_id': warn_template.id,
            'request_sla_failed_mail_template_id': fail_template.id,
        })
