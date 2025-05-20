{
    'name': "Generic Request Field Set",

    'summary': """
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.0.8.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/system_event_type.xml',
        'data/field_set_type.xml',

        'views/ir_model.xml',
        'views/request_classifier_view.xml',
        'views/request_request_view.xml',
        'views/test_incident_field_set_view.xml',
    ],

    'demo': [],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 10.0,
    'currency': 'EUR',
}
