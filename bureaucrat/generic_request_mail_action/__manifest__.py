{
    'name': "Generic Request Mail Action",

    'summary': """
        Provides easily operate by request stages through emails.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.0.4.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request_mail',
    ],

    # always loaded
    'data': [
        'data/mail_template.xml',

        'views/request_stage_route.xml',
    ],
    'demo': [
        'demo/request_stage_route.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 200.0,
    'currency': 'EUR',
}
