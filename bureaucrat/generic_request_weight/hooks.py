def _post_init_hook(env):
    env['request.request'].search([])._recompute_request_weight()
