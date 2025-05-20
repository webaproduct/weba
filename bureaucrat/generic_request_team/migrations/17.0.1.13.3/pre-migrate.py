from odoo.addons.generic_mixin.tools.migration_utils import ensure_version


@ensure_version('1.13.3')
def migrate(cr, installed_version):
    cr.execute("""
        DELETE FROM ir_ui_view WHERE id IN (
            SELECT res_id
            FROM ir_model_data
            WHERE model = 'ir.ui.view'
              AND module = 'generic_request_team'
              AND name = 'view_request_type_form_request_team_form'
        );
    """)
