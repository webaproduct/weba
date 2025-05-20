{
    'name': "Generic Request Todo ",

    'summary': """ Provides Todo tasks for Generic Request""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Todo',
    'version': '17.0.0.8.2',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
        'generic_todo',
    ],

    # always loaded
    'data': [
        'data/system_event_type.xml',
        'data/system_event_source_handler_map.xml',
        'views/request_request_view.xml',
    ],
    'demo': [
        'demo/generic_todo_template_demo.xml'
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'price': 20.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
