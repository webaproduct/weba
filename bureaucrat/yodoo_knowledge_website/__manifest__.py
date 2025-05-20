{
    'name': "Yodoo Knowledge Website",

    'summary': """
        Yodoo Knowledge Website
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'version': '17.0.0.11.0',
    # 'category': 'Knowledge',

    'depends': [
        'base',
        'base_setup',
        'website',
        'yodoo_knowledge',
    ],
    'data': [
        'data/website_data.xml',

        'templates/templates.xml',
        'views/yodoo_knowledge_item.xml',
    ],

    'assets': {
        # 'yodoo_knowledge_website.assets_knowledge_website': [
        #     ('include', 'web._assets_helpers'),
        #     ('include', 'web._assets_frontend_helpers'),
        #     'web/static/lib/jquery/jquery.js',
        #     'web/static/src/scss/pre_variables.scss',
        #     'web/static/lib/bootstrap/scss/_variables.scss',
        #     ('include', 'web._assets_bootstrap_frontend'),
        #     '/web/static/lib/odoo_ui_icons/*',
        #     '/web/static/lib/bootstrap/scss/_functions.scss',
        #     '/web/static/lib/bootstrap/scss/_mixins.scss',
        #     '/web/static/lib/bootstrap/scss/utilities/_api.scss',
        #     'web/static/src/libs/fontawesome/css/font-awesome.css',
        #     ('include', 'web._assets_core'),
        #
        #     ('include', 'web._assets_bootstrap_frontend'),
        #     'web/static/lib/bootstrap/js/dist/scrollspy.js',
        #     'web/static/src/legacy/js/libs/bootstrap.js',
        #
        #     'yodoo_knowledge_website/static/src/js/**/*',
        # ],
        'web.assets_frontend': [
            ('append', 'yodoo_knowledge_website/static/src/js/**/*'),
        ],
    },

    'images': ['static/description/banner.png'],

    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 150.0,
    'currency': 'EUR',
}
