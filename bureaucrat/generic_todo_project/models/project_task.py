import logging
from odoo import models

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = [
        'generic.todo.mixin.object',
        'project.task',
    ]
