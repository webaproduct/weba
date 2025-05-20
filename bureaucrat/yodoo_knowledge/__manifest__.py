{
    'name': "Yodoo Knowledge",

    'summary': """
        Yodoo Knowledge
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'version': '17.0.0.5.0',
    'category': 'Knowledge',

    'external_dependencies': {
        'python': [
            'html2text',
            'pdf2image',
        ],
        'bin': [
            'pdftoppm',
        ],
    },
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_field_m2m_view',
        'generic_mixin',
        'generic_tag',
        'mail',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/generic_tag_model.xml',
        'data/item_types_data.xml',
        'data/ir_actions_data.xml',

        'views/yodoo_knowledge_category.xml',
        'views/yodoo_knowledge_item.xml',
        'views/yodoo_knowledge_item_history.xml',
        'views/yodoo_knowledge_item_type.xml',
        'views/yodoo_knowledge_menu.xml',

        'templates/category_content.xml',
    ],
    'assets': {


        'yodoo_knowledge.assets_knowledge_item_menu': [
            # helpers


            'yodoo_knowledge/static/src/js/components/**/*',
            'yodoo_knowledge/static/src/js/services/**/*',
            'yodoo_knowledge/static/src/js/scss/knowledge_editor.scss',
            'yodoo_knowledge/static/src/js/utils/knowledge_utils.js',
            'yodoo_knowledge/static/src/js/xml/knowledge_editor.xml',
        ],

        'web.assets_backend': [
            'yodoo_knowledge/static/src/scss/knowledge_base.scss',

            ('include', 'yodoo_knowledge.assets_knowledge_item_menu'),
        ],
        # 'web.assets_frontend': [
        #     'yodoo_knowledge/static/src/scss/knowledge_base.scss',
        #
        #     ('include', 'yodoo_knowledge.assets_knowledge_item_menu'),
        # ],

        'yodoo_knowledge.assets_wysiwyg': [
            'yodoo_knowledge/static/src/js/wysiwyg.js',
            # 'yodoo_knowledge/static/src/js/knowledge_wysiwyg.js',
            # 'yodoo_knowledge/static/src/xml/knowledge_editor.xml',
            # 'yodoo_knowledge/static/src/xml/knowledge_article_templates.xml',
            # 'yodoo_knowledge/static/src/js/knowledge_clipboard_whitelist.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'demo': [
        'demo/res_groups.xml',
        'demo/yodoo_knowledge_base_demo.xml',
        'demo/yodoo_knowledge_base_items_demo.xml',
        'demo/yodoo_knowledge_demo.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 100.0,
    'currency': 'EUR',

}
