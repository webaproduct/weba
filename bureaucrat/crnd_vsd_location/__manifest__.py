{
    'name': 'Visualization Service Desk (Location)',
    'category': 'Service Desk',
    'summary': """
        Add address fields to Request Page on Service Desk.
    """,
    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'license': 'OPL-1',
    'version': '17.0.0.22.0',
    'depends': [
        'crnd_vsd',
        'generic_request_location',
    ],
    'data': [
        'templates/templates.xml',
        'views/request_classifier_view.xml',
    ],
    'assets': {
        'crnd_vsd.assets_request_widgets': [
            'crnd_vsd_location/static/src/js/vsd_js/**/*',
        ]
    },
    'installable': True,
}
