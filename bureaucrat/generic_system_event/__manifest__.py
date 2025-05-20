{
    'name': "Generic System Event",

    'summary': """
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic System Event',
    'version': '17.0.0.33.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'generic_mixin',
        'generic_m2o',
    ],

    # always loaded
    'data': [
        'data/generic_system_event_category.xml',
        'data/generic_system_event_type.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/system_event.xml',
        'views/system_event_category.xml',
        'views/system_event_source.xml',
        'views/system_event_type.xml',
        'views/system_event_menus.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'price': 30.0,
    'currency': 'EUR',
}
