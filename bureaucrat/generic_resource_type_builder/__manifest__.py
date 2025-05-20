{
    'name': "Generic Resource Type Builder",

    'summary': """
        Provides the ability to create resource types
        from UI.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Resource',
    'version': '17.0.1.4.3',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_resource',
        'crnd_web_on_create_action',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/generic_resource_type_views.xml',

        'wizard/generic_resource_type_wizard_create.xml',
    ],
    'demo': [
        'demo/demo_resource_users.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'price': 500.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
