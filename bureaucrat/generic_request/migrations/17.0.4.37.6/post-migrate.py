from odoo.addons.generic_mixin.tools.migration_utils import (
    ensure_version,
)


@ensure_version('4.37.6')
def migrate(cr, installed_version):
    cr.execute("""
            UPDATE request_request rr
            SET classifier_id = (
                SELECT rc.id FROM request_classifier rc
                WHERE
                    rc.service_id IS NOT DISTINCT FROM rr.service_id
                    AND rc.category_id IS NOT DISTINCT FROM rr.category_id
                    AND rc.type_id IS NOT DISTINCT FROM rr.type_id
            )
        """)
