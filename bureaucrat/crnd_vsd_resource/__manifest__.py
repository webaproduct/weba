{
    'name': 'Visualization Service Desk (Resource)',
    'category': 'Service Desk',
    'summary': 'Tag support in Website Service Desk',
    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'license': 'OPL-1',
    'version': '17.0.0.11.0',
    'depends': [
        'crnd_vsd',
        'generic_request_resource',
    ],
    'data': [
        'templates/templates.xml',
        'views/request_classifier_view.xml',
    ],

    'assets': {
        'crnd_vsd.assets_request_widgets': [
            'crnd_vsd_resource/static/src/js/vsd_js/**/*',
        ]
    },

    'installable': True,
}
