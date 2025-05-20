{
    'name': "Yodoo Knowledge MultiLanguage Website",

    'summary': """
        Yodoo Knowledge Website
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'version': '17.0.0.5.0',
    # 'category': 'Knowledge',

    'depends': [
        'yodoo_knowledge_website',
        'yodoo_knowledge_multilanguage',
    ],

    'assets': {
        'web.assets_frontend': [
            ('append',
             'yodoo_knowledge_multilanguage_website/static/src/js/**/*'),
        ],
    },

    'images': ['static/description/banner.png'],

    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 1.0,
    'currency': 'EUR',
}
