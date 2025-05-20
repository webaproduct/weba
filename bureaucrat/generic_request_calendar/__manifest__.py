{
    'name': "Generic Request Calendar",

    'summary': """
        Add ability to create calendar event from requests.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.0.17.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
        'calendar',
    ],

    # always loaded
    'data': [
        'views/request_request_view.xml',
    ],
    'demo': [
        'demo/request_calendar_demo.xml',
    ],

    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 20.0,
    'currency': 'EUR',
    'images': ['static/description/banner.png'],
}
