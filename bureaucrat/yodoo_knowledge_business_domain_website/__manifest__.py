{
    'name': "Yodoo Knowledge + Bussiness Domain (Website)",

    'summary': """
        Yodoo Knowledge + Bussiness Domain (Website)
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'version': '17.0.0.4.0',
    # 'category': 'Knowledge',

    'depends': [
        'yodoo_knowledge_website',
        'yodoo_knowledge_business_domain',
    ],

    'assets': {
        'web.assets_frontend': [
            ('append',
             'yodoo_knowledge_business_domain_website/static/src/js/**/*'),
        ],
    },

    'images': ['static/description/banner.png'],

    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 1.0,
    'currency': 'EUR',
}
