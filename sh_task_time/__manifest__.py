# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Task Timer",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "0.0.3",
    "category": "Project",
    "summary": "task timer, manage task time app, countdown timer module, calculate task start time, calculate work stop time, manage work time duration, time report timer, calculate work time, calculate task time Task Timer module Task Time Tracking Software Timer for Tasks Project Task Timer Task Time Management system Task Timer Management system Task Duration Monitoring Software Task Time Recording Task Timer App for Productivity Time Management Tool Odoo",
    "description": """This module allows the user to start/stop the time of a task. Easy to calculate the duration of time taken for the task.""",

    "depends": [
        'project',
        'hr_timesheet',
        'analytic'
    ],
    "data": [
        'security/sh_task_time_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/project_task_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sh_task_time/static/src/js/time_track.js',
            'sh_task_time/static/src/xml/TaskTimeCounter.xml',
            'sh_task_time/static/src/scss/time_track.scss'
        ],


    },
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "9",
    "currency": "EUR"
}
