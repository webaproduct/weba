{
    'name': "Yodoo Bussiness Domain",

    'summary': """
        Yodoo Bussiness Domain
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'version': '17.0.0.3.0',
    # 'category': 'Knowledge',

    'depends': [
        'base',
        'generic_rule',
    ],

    'data': [
        'security/ir.model.access.csv',

        'views/yodoo_business_domain_view.xml',
    ],
    'images': ['static/description/banner.png'],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
