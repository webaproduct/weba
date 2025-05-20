{
    'name': "Generic Request Team",

    'summary': """
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Assignment',
    'version': '17.0.1.13.4',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
        'generic_team',
    ],

    # always loaded
    'data': [
        'security/security.xml',

        'data/system_event_type.xml',
        'data/request_mail_templates_defaut.xml',
        'wizard/request_wizard_assign.xml',
        'views/request_request_views.xml',
        'views/generic_team.xml',
        'views/request_event.xml',
        'views/request_classifier.xml',

        'reports/request_graph_reports.xml',
        'reports/request_timesheet_report.xml',
    ],
    'images': ['static/description/banner.png'],
    'demo': [],

    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 10.0,
    'currency': 'EUR',
}
