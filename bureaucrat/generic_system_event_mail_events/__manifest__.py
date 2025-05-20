{
    'name': "Generic System Event (Mail Events)",

    'summary': """
        Make available events related to mail messages and mail activities.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic System Event',
    'version': '17.0.0.14.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_system_event',
        'mail',
    ],

    # always loaded
    'data': [
        'data/generic_system_event_category.xml',
        'data/generic_system_event_type.xml',
        'views/generic_system_event.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 10.0,
    'currency': 'EUR',
}
