from odoo.addons.generic_request.tests.common import RequestCase
from odoo import fields, Command


class TestFieldSet(RequestCase):
    def setUp(self):
        super(TestFieldSet, self).setUp()
        self.fs_test_model = self.env.ref(
            'generic_request_field_set.model_test_incident_field_set_value')
        self.FSType = self.env['field.set.type']

    def test_field_set_event(self):
        # Create field set type
        test_field_set = self.FSType.create({
            'name': 'Test field set',
            'field_set_model_id': self.fs_test_model.id,
        })

        classifier = self.ensure_classifier(
            category=self.tec_configuration_category,
            request_type=self.simple_type)
        self.assertFalse(classifier.field_set_type_id)

        # Add field set to classifier
        classifier.write({
            'field_set_type_id': test_field_set.id,
        })
        self.assertEqual(classifier.field_set_type_id, test_field_set)

        # Create request
        request = self.env['request.request'].create({
            'category_id': classifier.category_id.id,
            'type_id': classifier.type_id.id,
            'request_text': 'Test field set'
        })

        # Check no events about fieldset creation generated
        events = self.env['request.event'].search(
            [('request_id', '=', request.id)])
        request_events = events.mapped('event_code')
        self.assertNotIn('fieldset-created', request_events)

        # Create fieldset record
        self.env[self.fs_test_model.model].create({
            'request_id': request.id,
            'char_1': 'Test char',
            'integer_1': 15,
            'float_1': 14.32,
            'date_1': fields.Date.today(),
            'datetime_1': fields.Datetime.now(),
            'many2one_1_id': self.env.ref('base.partner_demo').id,
            'many2many_1_ids': [Command.set(
                [self.env.ref('base.partner_demo').id,
                 self.env.ref('base.partner_admin').id]
            )]
        })
        request_fieldset_values = request.field_set_values_record
        self.assertTrue(request_fieldset_values)
        self.assertEqual(
            request_fieldset_values._name,
            self.fs_test_model.model)

        # Check event fieldset-created generated for request
        events = self.env['request.event'].search(
            [('request_id', '=', request.id)])
        fieldset_create_event = events.filtered(
            lambda x: x.event_code == 'fieldset-created')
        self.assertEqual(len(fieldset_create_event), 1)
