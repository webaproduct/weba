{
    'name': "Generic Request (Address)",

    'summary': """
        Add address fields to request
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.0.4.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
    ],

    # always loaded
    'data': [
        'views/request_request.xml',
    ],
    'demo': [],

    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
    'price': 10.0,
    'currency': 'EUR',
}
