{
    'name': "Generic Request Action Team",

    'summary': """
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Assignment',
    'version': '17.0.0.8.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request_action',
        'generic_request_team',
    ],

    # always loaded
    'data': [
        'views/request_event_action.xml',
    ],
    'images': ['static/description/banner.png'],
    'demo': [],

    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 20.0,
    'currency': 'EUR',
}
