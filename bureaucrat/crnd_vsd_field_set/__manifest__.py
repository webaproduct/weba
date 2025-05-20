{
    'name': 'Visualization Service Desk (Field Set)',
    'category': 'Service Desk',
    'summary': """
        Add address fields to Request Page on Service Desk.
    """,
    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'license': 'OPL-1',
    'version': '17.0.0.23.0',
    'depends': [
        'crnd_vsd',
        'generic_request_field_set',
    ],
    'data': [
        'templates/templates.xml',
        'views/request_classifier_view.xml',
    ],
    'external_dependencies': {
        'python': [
            'defusedxml',
        ],
    },

    'assets': {
        'crnd_vsd.assets_request_widgets': [
            'crnd_vsd_field_set/static/src/js/vsd_js/**/*',
        ]
    },
    'installable': True,
}
