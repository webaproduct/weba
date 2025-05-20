{
    'name': "Generic Request Message Status",

    'summary': """
        Generic Request Message Status
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.0.13.1',

    'depends': [
        'generic_request',
    ],

    'data': [
        'security/security.xml',

        'views/request_request_view.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'generic_request_message_status/static/src/scss/'
            'request_kanban.scss',
        ],
    },

    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 20.0,
    'currency': 'EUR',
}
