{
    'name': "Generic Request HR",

    'summary': """
        Generic Request HR
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.0.5.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
        'hr',
    ],

    # always loaded
    'data': [
        'views/hr_employee_view.xml',
        ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'qweb': [],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 5.0,
    'currency': 'EUR',
}
