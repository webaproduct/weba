import logging

from odoo import models, fields
from odoo.addons.generic_mixin import post_create

_logger = logging.getLogger(__name__)


class GenericRequestFieldTableMixin(models.AbstractModel):
    _name = 'generic.request.field.table.mixin'
    _inherit = 'generic.mixin.track.changes'
    _description = 'Generic Request Field Table (Mixin)'

    request_id = fields.Many2one(
        'request.request', required=True, readonly=True, ondelete='cascade',
        string='Fields set values for request'
    )

    @post_create()
    def _post_create_request_id_trigger_event(self, changes):
        if self.request_id:
            self.request_id.trigger_event('fieldtable-created')
