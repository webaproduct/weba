{
    'name': "Generic Request Location",

    'summary': """
        Generic Request Location
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Request',
    'version': '17.0.0.17.2',

    'depends': [
        'generic_request',
        'generic_location',
    ],

    'data': [
        'views/generic_location_views.xml',
        'views/request_classifier_view.xml',
        'views/request_request.xml',

        'reports/request_graph_reports.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'price': 20.0,
    'currency': 'EUR',
}
