from odoo import api, SUPERUSER_ID
from odoo.addons.generic_mixin.tools.migration_utils import (
    ensure_version,
)


@ensure_version('1.13.3')
def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    classifiers = env['request.classifier'].search([])

    template = env.ref(
        'generic_request_team.mail_template_default_request_team_assigned')

    for classifier in classifiers:
        classifier.write({
            'request_team_assigned_mail_template_id': template.id,
        })
