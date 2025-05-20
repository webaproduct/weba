from odoo import models, fields, api, exceptions, _
from odoo.addons.http_routing.models.ir_http import slugify


class GenericResourceTypeWizardCreate(models.TransientModel):
    _name = 'generic.resource.type.wizard.create'
    _description = 'Resource Wizard: Create Type'

    def _default_groups(self):
        default_groups = self.env['res.groups'].browse()
        default_groups += self.env.ref(
            'generic_resource.group_generic_resource_user_implicit',
            raise_if_not_found=False) or default_groups
        default_groups += self.env.ref(
            'generic_resource.group_generic_resource_user',
            raise_if_not_found=False) or default_groups
        default_groups += self.env.ref('base.group_portal')
        default_groups += self.env.ref('base.group_public')
        return default_groups

    name = fields.Char(required=True)
    model = fields.Char(required=True)
    enable_chatter = fields.Boolean(default=False)
    enable_mail_activity = fields.Boolean(default=False)
    model_group_ids = fields.Many2many(
        'res.groups', string='Model Groups', default=_default_groups)

    @api.onchange('name')
    def _onchange_name_set_model(self):
        for record in self:
            if record.name:
                record.model = slugify(
                    'x_%s' % record.name or '', max_length=0).replace('-', '_')

    # ///Model part///
    def _prepare_model_values(self):
        return {
            'name': self.name,
            'model': self.model,
            'generic_resource_code': slugify(self.name),
            'is_generic_resource': True,
            'is_mail_thread': self.enable_chatter,
            'is_mail_activity': self.enable_mail_activity,
        }

    def _create_model(self, values):
        model = self.env['ir.model'].sudo().create(values)

        # Create model data to generate xml_id
        self.env['ir.model.data'].create({
            'module': '__generic_resource_type_builder__',
            'name': 'model_%s' % model.model,
            'model': 'ir.model',
            'res_id': model.id,
        })
        return model

    # ///Access part///
    def _create_model_access(self, model):
        ACL = self.env['ir.model.access']
        group_resource_user_implicit = self.env.ref(
            'generic_resource.group_generic_resource_user_implicit',
            raise_if_not_found=False)
        group_resource_user = self.env.ref(
            'generic_resource.group_generic_resource_user',
            raise_if_not_found=False)
        group_portal_user = self.env.ref('base.group_portal')
        group_public_user = self.env.ref('base.group_public')
        acl_ids = ACL.browse()
        if group_resource_user_implicit:
            acl_ids += ACL.sudo().create({
                'name': group_resource_user_implicit.name,
                'model_id': model.id,
                'group_id': group_resource_user_implicit.id,
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False
            })
        if group_resource_user:
            acl_ids += ACL.sudo().create({
                'name': group_resource_user.name,
                'model_id': model.id,
                'group_id': group_resource_user.id,
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True
            })
        # Add groups of portal and public users by default. Resource
        # visibility can be set on resource by 'Resource visibility'
        # field.
        acl_ids += ACL.sudo().create({
            'name': group_portal_user.name,
            'model_id': model.id,
            'group_id': group_portal_user.id,
            'perm_read': True,
            'perm_write': False,
            'perm_create': False,
            'perm_unlink': False
        })
        acl_ids += ACL.sudo().create({
            'name': group_public_user.name,
            'model_id': model.id,
            'group_id': group_public_user.id,
            'perm_read': True,
            'perm_write': False,
            'perm_create': False,
            'perm_unlink': False
        })

        # Create model data to generate xml_id
        self.env['ir.model.data'].create({
            'module': '__generic_resource_type_builder__',
            'name': 'access_%s_%s' % (
                model.model,
                acl.name.replace('.', '_').replace(' ', '_').lower()),
            'model': 'ir.model.access',
            'res_id': acl.id} for acl in acl_ids)

    # ///Dispatcher///
    def action_do_create_resource_type(self):
        if not self.env.user.has_group("base.group_system"):
            raise exceptions.AccessError(
                _("The only users '%(group_system)s' "
                  "group have permissions to create '%(resource_type)s'!")
                % {'group_system':
                   self.env.ref('base.group_system').display_name,
                   'resource_type': 'Resource Type'})
        model_values = self._prepare_model_values()
        model = self._create_model(model_values)
        model.resource_type_id._create_model_views(model)
        self._create_model_access(model)
        return self.env['generic.mixin.get.action'].get_form_action_by_xmlid(
            xmlid='generic_resource.generic_resource_type_action',
            context={'active_id': model.resource_type_id.id},
            res_id=model.resource_type_id.id)
