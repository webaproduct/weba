from odoo.tools import SQL


def _post_init_hook(env):
    resource_type = env['generic.resource.type']

    for resource_type_element in resource_type.search([]):

        sql_query = """
            INSERT INTO ir_act_window
                   (name, res_model, binding_type,
                    view_mode, target, context,
                    domain, type, binding_model_id)
            SELECT name, res_model, binding_type,
                   view_mode, target, context,
                   domain, type, %s
            FROM ir_act_window
            WHERE id = %s
            RETURNING id;
        """

        env.cr.execute(
            SQL(sql_query,
                resource_type_element.model_id.id,
                env.ref(
                    'generic_resource_role.'
                    'action_resource_open_wizard_manage_roles').id)
        )

        action_id = env.cr.fetchone()[0]
        resource_type_element.write({
            'resource_act_manage_roles_id': action_id,
        })
