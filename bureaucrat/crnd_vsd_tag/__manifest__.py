{
    'name': 'Visualization Service Desk (Tag)',
    'category': 'Service Desk',
    'summary': 'Tag support in Website Service Desk',
    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'license': 'OPL-1',
    'version': '17.0.0.10.0',
    'depends': [
        'crnd_vsd',
        'generic_request',
    ],
    'data': [
        'templates/templates.xml',
        'views/request_classifier_view.xml',
    ],
    'demo': [
        'demo/request_type_generic.xml',
    ],

    'assets': {
        'crnd_vsd.assets_request_widgets': [
            'crnd_vsd_tag/static/src/js/vsd_js/**/*',
        ]
    },

    'installable': True,
}
