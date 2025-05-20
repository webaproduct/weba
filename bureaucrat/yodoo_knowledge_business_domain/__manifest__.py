{
    'name': "Yodoo Knowledge + Bussiness Domain",

    'summary': """
        Yodoo Knowledge + Bussiness Domain
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'version': '17.0.0.3.0',
    # 'category': 'Knowledge',

    'depends': [
        'yodoo_knowledge',
        'yodoo_business_domain',
    ],
    'data': [
        'views/yodoo_knowledge_category.xml',
        'views/yodoo_knowledge_item.xml',
    ],
    'images': ['static/description/banner.png'],

    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 1.0,
    'currency': 'EUR',
}
