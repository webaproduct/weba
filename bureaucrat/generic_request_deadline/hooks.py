# This hook is needed to synchronize 'deadline_set' field of this module with
# 'deadline_date' field and set 'deadline_set' to True if request has
# deadline date.
def _post_init_hook(env):
    env['request.request'].search([
        ('deadline_set', '=', False), ('deadline_date', '!=', False)]).write({
            'deadline_set': True,
        })
