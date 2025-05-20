{
    'name': "Generic Request (Resource)",

    'summary': """
    Provides integration between Generic Resource
    and Generic Request modules.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.2.11.5',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
        'generic_resource',
        'generic_m2o',
    ],

    # always loaded
    'data': [
        'views/generic_resource_view.xml',
        'views/request_request_view.xml',
        'views/request_classifier_view.xml',
        'data/system_event_type.xml',
        'views/request_event.xml',

        'reports/request_graph_reports.xml',
    ],
    'demo': [
        'demo/request_type_seq.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'OPL-1',
    'price': 20.0,
    'currency': 'EUR',
}
