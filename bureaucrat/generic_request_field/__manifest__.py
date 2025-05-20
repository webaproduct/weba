{
    'name': "Generic Request Field",

    'summary': """
        Add configurable fields to requests
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.3.33.3',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
        'http_routing',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/request_field_view.xml',
        'views/request_type_view.xml',
        'views/request_request_view.xml',

        'wizard/request_wizard_close.xml',
    ],
    'demo': [
        'demo/request_type_create_lxc.xml',
        'demo/request_type_field.xml',
        'demo/request_classifier.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'generic_request_field/static/src/scss/request_field.scss',

            'generic_request_field/static/src/js/request_fields.js',
            'generic_request_field/static/src/js/request_fields.xml',
        ],
    },

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 50.0,
    'currency': 'EUR',
}
