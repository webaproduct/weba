import logging
from odoo import exceptions, Command
from odoo.addons.generic_request.tests.common import RequestCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestGenericRequestTodo(RequestCase):

    @classmethod
    def setUpClass(cls):
        super(TestGenericRequestTodo, cls).setUpClass()

    def test_unlink_request(self):
        self.assertFalse(self.request_2.generic_todo_ids)

        vals_todo = {
            'name': 'Test Todo Request Unlink',
            'todo_type_id': self.env.ref(
                'generic_todo.generic_todo_type_simple').id,
        }

        self.request_2.write({
            'generic_todo_ids': [Command.create({**vals_todo})],
        })
        self.assertTrue(self.request_2.generic_todo_ids)

        with self.assertRaises(exceptions.UserError):
            self.request_2.unlink()

        todos = self.request_2.generic_todo_ids
        todos.unlink()
        self.assertFalse(self.request_2.generic_todo_ids)
        self.request_2.unlink()
