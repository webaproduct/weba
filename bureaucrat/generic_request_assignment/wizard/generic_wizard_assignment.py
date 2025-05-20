import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class GenericWizardAssign(models.TransientModel):
    _inherit = 'generic.wizard.assign'

    @api.model
    def default_get(self, fields_list):
        res = super(GenericWizardAssign, self).default_get(fields_list)

        model = res.get('assign_model', False)
        if model and model == 'request.request':
            res.update({
                'unsubscribe_prev_assignee': (
                    self.env.user.company_id.
                    request_autoset_unsubscribe_prev_assignee),
            })

        return res

    def _do_assign_user(self, assign_obj):
        if assign_obj._name != 'request.request':
            return super(GenericWizardAssign, self)._do_assign_user(assign_obj)
        # If neither user_id nor responsible_id is set
        # and autoset_responsible is enabled,
        # set responsible to the current user.
        company = self.env.user.company_id
        autoset_responsible = company.request_autoset_responsible_person
        if (not assign_obj.user_id and not assign_obj.responsible_id
                and autoset_responsible):
            assign_obj.write({
                'responsible_id': self.env.user.id,
            })
        return super(GenericWizardAssign, self)._do_assign_user(assign_obj)
