from odoo.addons.generic_mixin.tools.migration_utils import (
    ensure_version,
)


@ensure_version('1.6.0')
def migrate(cr, installed_version):
    cr.execute("""
        INSERT INTO ir_config_parameter
            (key, value)
        SELECT 'generic_request_weight.request_sort_direction',
               c.request_date_related_sort_direction
        FROM res_company AS C
        ORDER BY id ASC
        ON CONFLICT DO NOTHING;
    """)
