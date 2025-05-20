import psycopg2
from odoo.tests.common import Form
from odoo.tools import mute_logger
from odoo import exceptions
from .common import RequestCase


class TestRequestClassifier(RequestCase):
    def setUp(self):
        super(TestRequestClassifier, self).setUp()
        self.test_classifier = self.env.ref(
            'generic_request.classifier_request_type_'
            'simple_category_service_default_demo_resource')
        self.test_service = self.env.ref(
            'generic_service.generic_service_default')
        self.test_category = self.env.ref(
            'generic_request.request_category_demo_resource')
        self.test_category_2 = self.env.ref(
            'generic_request.request_category_demo')
        self.test_type = self.env.ref(
            'generic_request.request_type_simple')

    @mute_logger('odoo.sql_db')
    def test_classifier_delete_edit(self):
        # Check no related requests in classifier
        self.assertFalse(self.test_classifier.request_ids)
        # Enable services
        self.env.ref('base.group_user').write(
            {'implied_ids': [(4, self.env.ref(
                'generic_request.group_request_use_services').id)]})

        with Form(self.env['request.request']) as request:
            request.service_id = self.test_service
            request.category_id = self.test_category
            request.type_id = self.test_type
            request.request_text = 'Test classifier'
            request.save()
        request_record = self.env['request.request'].browse(request.id)
        self.assertTrue(self.test_classifier.request_ids)
        self.assertEqual(self.test_classifier.request_ids_count, 1)
        self.assertIn(request_record.id, self.test_classifier.request_ids.ids)
        self.assertEqual(request_record.classifier_id, self.test_classifier)

        # Try edit request classifier, that has related requests
        with self.assertRaises(exceptions.UserError):
            self.test_classifier.category_id = self.test_category_2
        with self.assertRaises(psycopg2.errors.ForeignKeyViolation):
            self.test_classifier.unlink()

        # Try edit, delete classifier after deleting related request
        self.test_classifier.request_ids.unlink()
        self.test_classifier.category_id = self.test_category_2
        self.test_classifier.unlink()

    def test_request_edit_classifiers(self):
        test_service2 = self.env['generic.service'].create({
            'name': 'service',
            'code': 'service',
        })

        # Try create request without existing classifier
        not_existing_classifier = self.Classifier.search([
            ('service_id', '=', test_service2.id),
            ('category_id', '=', self.test_category.id),
            ('type_id', '=', self.test_type.id)])
        self.assertFalse(not_existing_classifier.exists())

        with self.assertRaises(exceptions.ValidationError):
            self.env['request.request'].create({
                'service_id': test_service2.id,
                'category_id': self.test_category.id,
                'type_id': self.test_type.id,
                'request_text': 'Test classifier'
            })
        # Create classifier
        classifier = self.env['request.classifier'].create({
            'service_id': test_service2.id,
            'category_id': self.test_category.id,
            'type_id': self.test_type.id
        })
        # Try create request again after classifier creation
        request = self.env['request.request'].create({
            'service_id': test_service2.id,
            'category_id': self.test_category.id,
            'type_id': self.test_type.id,
            'request_text': 'Test classifier'
        })
        # Try edit request on unexisting classifier
        with self.assertRaises(exceptions.ValidationError):
            request.write({
                'category_id': self.test_category_2.id
            })
        self.assertEqual(request.classifier_id, classifier)
