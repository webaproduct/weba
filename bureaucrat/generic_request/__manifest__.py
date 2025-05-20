# flake8: noqa: E501
{
    'name': "Generic Request",

    'summary': """
        Incident management and helpdesk system - logging, recording,
        tracking, addressing, handling and archiving
        issues that occur in daily routine.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Request',
    'version': '17.0.4.39.0',
    'external_dependencies': {
        'python': [
            'html2text',
        ],
    },

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'generic_mixin',
        'generic_service',
        'generic_tag',
        'generic_system_event',
        'crnd_web_diagram_plus',
        'crnd_web_tree_colored_field',
        'base_setup',
        'base_field_m2m_view',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/request_sequence.xml',
        'data/mail_subtype.xml',
        'data/request_stage_type.xml',
        'data/generic_tag_model.xml',
        'data/generic_tag_category.xml',
        'data/generic_tag.xml',
        'data/request_timesheet_activity.xml',
        'data/request_channel.xml',
        'data/ir_cron.xml',

        'views/generic_service.xml',
        'views/request_views.xml',
        'views/res_config_settings_view.xml',
        'views/request_category_view.xml',
        'views/request_type_view.xml',
        'views/request_kind.xml',
        'views/request_service.xml',
        'views/request_stage_route_view.xml',
        'views/request_stage_view.xml',
        'views/request_stage_type_view.xml',
        'views/request_request_view.xml',
        'views/request_channel_view.xml',
        'views/request_classifier_view.xml',
        'views/res_partner_view.xml',
        'views/res_users.xml',
        'views/mail_template_view.xml',
        'views/request_event.xml',
        'views/request_creation_template.xml',
        'views/generic_tag_menu.xml',
        'views/request_timesheet_activity.xml',
        'views/request_timesheet_line.xml',
        'views/request_mail_templates_menu.xml',
        'views/mail_mail_views.xml',
        'wizard/request_wizard_close.xml',
        'wizard/request_wizard_assign.xml',
        'wizard/request_wizard_stop_work.xml',
        'wizard/request_wizard_set_parent.xml',
        'wizard/request_wizard_responsible.xml',

        'reports/request_timesheet_report.xml',
        'reports/request_graph_reports.xml',

        'data/request_mail_templates_default.xml',
        'data/system_event_source.xml',
        'data/system_event_category.xml',
        'data/system_event_type.xml',
    ],

    'demo': [
        'demo/response_attachments.xml',
        'demo/request_demo_users.xml',
        'demo/request_category_demo.xml',
        'demo/request_kind.xml',
        'demo/request_type_simple.xml',
        'demo/request_type_seq.xml',
        'demo/request_type_access.xml',
        'demo/request_type_non_ascii.xml',
        'demo/request_type_with_complex_priority.xml',
        'demo/request_type_reopen.xml',
        'demo/request_classifier.xml',
        'demo/request_mail_activity.xml',
        'demo/request_creation_template.xml',
        'demo/demo_request_timesheet_activity.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'generic_request/static/src/scss/request_timesheet.scss',
            'generic_request/static/src/scss/request_form.scss',
            'generic_request/static/src/scss/request_tree.scss',
            'generic_request/static/src/scss/request_kanban.scss',
            'generic_request/static/src/scss/request_dashboard_kanban.scss',

            'generic_request/static/src/js/stage_route_out/stage_buttons.js',
            'generic_request/static/src/js/stage_route_out/stage_buttons.xml',
        ],
    },

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 50.0,
    'currency': 'EUR',
}
