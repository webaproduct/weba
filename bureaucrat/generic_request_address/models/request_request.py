from odoo import models, fields, api
from odoo.addons.generic_mixin import pre_write


class RequestRequest(models.Model):
    _inherit = 'request.request'

    # Add address fields
    address_street = fields.Char('Street')
    address_street2 = fields.Char('Street2')
    address_zip = fields.Char('Zip', change_default=True)
    address_city = fields.Char('City')
    address_state_id = fields.Many2one("res.country.state", string='State')
    address_country_id = fields.Many2one('res.country', string='Country')

    @api.onchange('address_state_id')
    def _onchange_addres_state(self):
        if self.address_state_id:
            self.address_country_id = self.address_state_id.country_id.id

    @api.onchange('address_country_id')
    def _onchange_address_country_id(self):
        res = {'domain': {'address_state_id': []}}
        if self.address_country_id:
            res['domain']['address_state_id'] = [
                ('country_id', '=', self.address_country_id.id),
            ]
        return res

    @pre_write('address_state_id', 'address_country_id')
    def _before_address_country_id_changed(self, changes):
        """This method clean a field or clean value of address_state_id
           if that state does not belong to the specified country.
       """
        # TODO: Maybe need more validations?
        if not changes.get('address_country_id', False):
            return {}
        new_country = changes['address_country_id'].new_val
        state = False
        if changes.get('address_state_id', False):
            state = changes['address_state_id'].new_val
        if not state:
            state = self.address_state_id
        if state and state.country_id.id != new_country.id:
            return {
                'address_state_id': False
            }
        return {}
