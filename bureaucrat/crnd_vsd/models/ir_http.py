from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        modules = super(IrHttp, cls)._get_translation_frontend_modules_name()
        return modules + ['crnd_vsd']
