{
    'name': "Generic Request Weight",

    'summary': """
        Allows you to automatically sort requests by predefined rules
        depending on SLA, Priority, Kanban State, Request Type, etc.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.1.12.2',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request_sla',
        'generic_request_mail',
    ],

    # always loaded
    'data': [
        'views/request_type_view.xml',
        'views/request_stage_view.xml',
        'views/request_category_view.xml',
        'views/request_request_view.xml',
        'views/generic_service_views.xml',
        'views/generic_service_level_views.xml',
        'views/res_config_settings_view.xml',
    ],
    'demo': [],

    'images': ['static/description/banner.png'],
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
    'price': 100.0,
    'currency': 'EUR',
}
