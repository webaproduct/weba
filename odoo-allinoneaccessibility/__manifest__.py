# -*- encoding: utf-8 -*-
{
    'name': 'All in One Accessibility',
    'category': "Website",
    'version': '1.1',
    'license': 'OPL-1',
    'summary': 'All in One Accessibility widget is based on assistive technology and AI that helps organizations enhance the accessibility and usability of their website quickly',
    'description': 'All in One Accessibility widget improves Odoo website ADA compliance and browser experience for ADA, WCAG 2.1, Section 508, Australian DDA, European EAA EN 301 549, UK Equality Act (EA), Israeli Standard 5568, California Unruh, Ontario AODA, Canada ACA, German BITV, and France RGAA Standards',
    'author': 'Skynet Technologies USA LLC',
    'website':'https://www.skynettechnologies.com/all-in-one-accessibility',
    'depends': ['base', 'base_setup', 'web'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'templates/base_url_passing.xml',

    ],
    'qweb': [
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': True,
    'support':'hello@skynettechnologies.com',
}

