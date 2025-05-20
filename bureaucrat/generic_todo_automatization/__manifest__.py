{
    'name': "Generic Todo Automatization",

    'summary': """ Provides Automatization for Todo tasks""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Todo',
    'version': '17.0.0.4.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_todo',
    ],

    # always loaded
    'data': [
        'views/generic_todo_views.xml',
        'views/generic_todo_template_line_views.xml',

        'wizard/todo_wizard_add_template_views.xml',
    ],
    'demo': [
        'demo/generic_todo_template_demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'price': 30.0,
    'currency': 'EUR',
}
