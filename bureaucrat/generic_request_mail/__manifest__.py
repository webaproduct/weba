{
    'name': "Generic Request (mail integration)",

    'summary': """
        Easily manage mails sources to create requests.
        Create requests from incoming email in one click.
        Setup canned responses for chatter and messages.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.2.10.4',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
        'generic_condition',
        'generic_system_event_mail_events',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/request_mail.xml',
        'views/request_mail_source.xml',
        'views/request_request.xml',
        'views/fetchmail_server.xml',
        'views/res_config_settings.xml',
    ],
    'demo': [
        'demo/request_creation_template.xml',
        'demo/request_mail_source.xml',
        'demo/request_request.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 10.0,
    'currency': 'EUR',
}
