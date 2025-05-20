from odoo.addons.generic_mixin.tests.common import FindNew
from odoo.tests.common import TransactionCase


class TestAutomatization(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAutomatization, cls).setUpClass()

        cls.Todo = cls.env['generic.todo']
        cls.todo_simple = cls.env.ref(
            'generic_todo.generic_todo_type_simple')
        cls.model_simple = cls.env.ref(
            'generic_todo.model_generic_todo_simple')

    def test_todo_auto_server_action(self):
        # Server action, that create contact
        # with the name "Post create name" just after creation
        post_create_server_action = self.env['ir.actions.server'].create({
            'name': 'Todo Simple post-create server action',
            'model_id': self.model_simple.id,
            'state': 'code',
            'code': "env['res.partner'].create("
                    "{'name': 'Post create ' + record.todo_type_id.name})",
        })
        # Server action, that create contact
        # with the same name as todos type on state 'In progress'
        pre_start_server_action = self.env['ir.actions.server'].create({
            'name': 'Todo Simple pre-start server action',
            'model_id': self.model_simple.id,
            'state': 'code',
            'code': "env['res.partner'].create("
                    "{'name': record.todo_type_id.name})",
        })

        # Server action, that create contact
        # with the same name as todos type on state 'Cancel'
        on_cancel_server_action = self.env['ir.actions.server'].create({
            'name': 'Todo Simple on-cancel server action',
            'model_id': self.model_simple.id,
            'state': 'code',
            'code': "env['res.partner'].create("
                    "{'name': record.todo_type_id.name})",
        })

        # Server action, that create contact with the name
        # "Test contact (todos completed)" on state 'Done'
        on_done_server_action = self.env['ir.actions.server'].create({
            'name': 'Todo Simple pre-start server action',
            'model_id': self.model_simple.id,
            'state': 'code',
            'code': "env['res.partner'].create("
                    "{'name': 'Test contact (todos completed)'})",
        })

        # Create todo
        # Check post create server action
        with FindNew(self.env, "res.partner") as nr:
            todo = self.Todo.create({
                'name': 'Test Todo',
                'todo_type_id': self.todo_simple.id,
                'post_create_server_action': post_create_server_action.id,
                'pre_start_server_action': pre_start_server_action.id,
                'on_done_server_action': on_done_server_action.id
            })
            self.assertEqual(todo.state, 'new')
        self.assertEqual(len(nr['res.partner']), 1)
        new_contact = nr['res.partner']
        self.assertTrue(new_contact.exists())
        self.assertEqual(
            new_contact.name, f'Post create {self.todo_simple.name}')

        # Start todos, check contact properly created
        with FindNew(self.env, "res.partner") as nr:
            todo.state = 'in_progress'
            self.assertEqual(todo.state, 'in_progress')
        new_contact = nr['res.partner']
        self.assertTrue(new_contact.exists())
        self.assertEqual(len(nr['res.partner']), 1)
        self.assertEqual(new_contact.name, self.todo_simple.name)

        # Done todos, check contact properly created
        with FindNew(self.env, "res.partner") as nr:
            todo.state = 'done'
            self.assertEqual(todo.state, 'done')
        new_contact = nr['res.partner']
        self.assertTrue(new_contact.exists())
        self.assertEqual(len(nr['res.partner']), 1)
        self.assertEqual(new_contact.name, 'Test contact (todos completed)')

        # Create todo
        # Check on cancel server action
        with FindNew(self.env, "res.partner") as nr:
            todo = self.Todo.create({
                'name': 'Test on cancel Todo',
                'todo_type_id': self.todo_simple.id,
                'on_cancel_server_action': on_cancel_server_action.id,
            })
            self.assertEqual(todo.state, 'new')
        self.assertEqual(len(nr['res.partner']), 0)

        # Start todos, check no contacts created
        with FindNew(self.env, "res.partner") as nr:
            todo.state = 'in_progress'
            self.assertEqual(todo.state, 'in_progress')
        self.assertEqual(len(nr['res.partner']), 0)

        # Cancel todos, check contact properly created
        with FindNew(self.env, "res.partner") as nr:
            todo.state = 'canceled'
            self.assertEqual(todo.state, 'canceled')
        new_contact = nr['res.partner']
        self.assertTrue(new_contact.exists())
        self.assertEqual(len(nr['res.partner']), 1)
        self.assertEqual(new_contact.name, self.todo_simple.name)
