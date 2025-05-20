from odoo.addons.generic_mixin.tools.migration_utils import (
    ensure_version,
    migrate_xmlids_to_module,
    cleanup_module_data,
)


@ensure_version('3.29.0')
def migrate(cr, installed_version):
    migrate_xmlids_to_module(
        cr,
        src_module='generic_request_field_service',
        dst_module='generic_request_field',
        models=[
            'ir.model.fields',
            'ir.model.constraint',
            'ir.model.relation',
            'ir.ui.menu',
            'ir.model.access',
            'ir.actions.act_window',
            'request.type',
        ],
        cleanup=True,
    )

    # Cleanup module data
    cleanup_module_data(cr, 'generic_request_field_service')
