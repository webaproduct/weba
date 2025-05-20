{
    'name': "Generic Request Deadline",

    'summary': """
        This module adds functionality of request deadline field,
        that allows users to track the history of changes made
        to the deadline, understand the reasoning behind each change
        and calculate deadline overdue time values.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Request',
    'version': '17.0.0.12.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_request',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/deadline_change_reason.xml',
        'data/cron_data.xml',

        'views/request_deadline_change_reason.xml',
        'views/request_event.xml',
        'views/request_request_view.xml',
        'views/request_type.xml',

        'wizard/request_wizard_change_deadline.xml'
    ],

    'qweb': [],
    'demo': [],

    'images': ['static/description/banner.png'],
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 30.0,
    'currency': 'EUR',
}
