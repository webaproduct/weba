# flake8: noqa: E501

{
    'name': 'Visualization Service Desk',
    'category': 'Service Desk',
    'summary': 'Website UI for Service Desk',
    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'license': 'OPL-1',
    'version': '17.0.0.35.0',

    'depends': [
        'base_setup',
        'mail',
        'website',
        'website_mail',
        'generic_request',
    ],
    'data': [
        'data/website_data.xml',
        'data/ir_module_category.xml',
        'templates/templates.xml',
        'security/security.xml',
        'views/request_stage_route.xml',
        'views/request_classifier_view.xml',
        'views/request_kind.xml',
        'views/request_request.xml',
        'views/res_config_settings.xml',
    ],
    'demo': [
        'demo/request_type_incident.xml',
        'demo/demo_res_users.xml',
        'demo/demo_category.xml',
        'demo/request_kind.xml',
        'demo/demo_generic_type.xml',
        'demo/demo_upgrade_type.xml',
        'demo/generic_service.xml',
        'demo/demo_request_type_seq.xml',
        'demo/demo_bug_report_type.xml',
        'demo/request_subrequests.xml',
        'demo/demo_type_no_service.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'crnd_vsd/static/src/xml/templates.xml',
        ],
        'crnd_vsd.assets_request_widgets': [
            ('include', 'web._assets_helpers'),
            ('include', 'web._assets_frontend_helpers'),
            'web/static/lib/jquery/jquery.js',
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            # ('include', 'web._assets_bootstrap_frontend'),
            '/web/static/lib/odoo_ui_icons/*',
            # '/web/static/lib/bootstrap/scss/_functions.scss',
            # '/web/static/lib/bootstrap/scss/_mixins.scss',
            # '/web/static/lib/bootstrap/scss/utilities/_api.scss',
            'web/static/src/libs/fontawesome/css/font-awesome.css',
            ('include', 'web._assets_core'),

            'web/static/src/core/autocomplete/*',
            'website/static/src/components/autocomplete_with_pages/*',
            'web/static/src/legacy/utils.js',
            'website/static/src/js/utils.js',

            'web_editor/static/src/js/frontend/loader_loading.js',
            ('include', 'web_editor.assets_media_dialog'),

            'web_editor/static/src/js/editor/odoo-editor/src/base_style.scss',
            'web_editor/static/src/js/common/**/*',
            'web_editor/static/src/js/editor/odoo-editor/src/utils/utils.js',
            'web_editor/static/src/js/wysiwyg/fonts.js',

            'web_editor/static/src/scss/web_editor.common.scss',
            # 'web_editor/static/src/scss/web_editor.frontend.scss',
            ('include', 'web_editor.assets_wysiwyg'),
            'web_editor/static/src/js/frontend/loadWysiwygFromTextarea.js',

            'crnd_vsd/static/src/js/**/*',
        ],
    },

    'external_dependencies': {
        'python': [
            'defusedxml',
        ],
    },

    'images': ['static/description/banner.png'],
    'installable': True,
}
