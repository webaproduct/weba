# -*- coding: utf-8 -*-
{
    'name': "Hide Website Element",

    'summary': """
        Hide Website Element
    """,

    'description': """
        Hide Website Element
    """,

    'author': "Volodymyr Babenko",
    'website': "",

    'category': '',
    'version': '0.1',

    'depends': ['project', 'portal', 'hr_timesheet'],
    'application': True,
    'installable': True,
    'data': [
        'views/project_portal_project_task_templates.xml',
        'views/project_task_portal_templates.xml',
    ],
    'license': 'AGPL-3'
}
