{
    'name': "Yodoo Knowledge + Multilanguage",

    'summary': """
        Yodoo Knowledge + Multilanguage
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'version': '17.0.0.3.0',
    # 'category': 'Knowledge',

    'depends': [
        'base',
        'yodoo_knowledge',
    ],
    'data': [
        'views/yodoo_knowledge_item.xml',
        'views/yodoo_knowledge_history_item.xml',
    ],
    'images': ['static/description/banner.png'],

    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 1.0,
    'currency': 'EUR',
}
