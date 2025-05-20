{
    'name': "Generic Todo Project",

    'summary': """ Provides Todo tasks for Project """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Todo',
    'version': '17.0.0.10.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_todo',
        'project',
    ],

    # always loaded
    'data': [
        'views/project_task_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 10.0,
    'currency': 'EUR',
}
