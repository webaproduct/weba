from odoo.tests.common import Form
from .common import RequestCase


class TestRequestTags(RequestCase):
    """Test request tags
    """
    def setUp(self):
        super(TestRequestTags, self).setUp()

        # Request service
        self.default_service = self.env.ref(
            'generic_service.generic_service_default')

        # Request category
        self.tech_categ = self.env.ref(
            'generic_request.request_category_demo_technical_configuration')
        # Tag categories
        self.tag_categ_severity = self.env.ref(
            'generic_request.tag_category_severity')
        self.tag_categ_priority = self.env.ref(
            'generic_request.tag_category_priority')
        self.tag_categ_platform = self.env.ref(
            'generic_request.tag_category_platform')

    def test_request_tags(self):
        # Enable services
        self.env.ref('base.group_user').write(
            {'implied_ids': [(4, self.env.ref(
                'generic_request.group_request_use_services').id)]})

        # PREPARE INIT TEST DATA
        # Add tag categories to the service
        # Check request tags domain
        with Form(self.env['request.request']) as request_form:

            # Check default domain
            self.assertListEqual(
                request_form.tag_ids_domain,
                ['&', ('model_id.model', '=', 'request.request'),
                 ('category_id', '=', False),
                 ])

            # Check tags domain with service
            request_form.service_id = self.default_service
            request_form.category_id = self.tech_categ
            request_form.type_id = self.access_type
            self.assertTrue(request_form.classifier_id)
            classifier_tag_categs = request_form.classifier_id.tag_category_ids
            self.assertListEqual(
                request_form.tag_ids_domain,
                ['&', ('model_id.model', '=', 'request.request'),
                 ('category_id', 'in', classifier_tag_categs.ids),
                 ])
            request_form.save()
