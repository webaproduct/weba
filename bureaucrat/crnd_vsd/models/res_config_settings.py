from odoo import models, fields
from lxml import etree


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    request_wsd_public_ui_visibility = fields.Selection(
        related='company_id.request_wsd_public_ui_visibility',
        readonly=False,
        string='Website Service Desk (Public Visibility)')
    request_wsd_public_use_author_phone = fields.Selection(
        related='company_id.request_wsd_public_use_author_phone',
        readonly=False,
        string='Website Service Desk (Use Author Phone)')

    request_limit_max_text_size = fields.Integer(
        related='company_id.request_limit_max_text_size', readonly=False)

    request_allowed_upload_file_types = fields.Char(
        related='company_id.request_allowed_upload_file_types',
        readonly=False)
    request_limit_max_upload_file_size = fields.Integer(
        related='company_id.request_limit_max_upload_file_size',
        readonly=False)
    request_limit_max_upload_file_size_uom = fields.Selection(
        related='company_id.request_limit_max_upload_file_size_uom',
        readonly=False)

    use_service_groups = fields.Boolean(
        related='website_id.use_service_groups',
        readonly=False,
        required=True)

    request_on_request_creating_redirect_to = fields.Selection(
        related='website_id.request_redirect_after_created_on_website',
        readonly=False,
        string='Redirect after request created on Website'
    )

    request_pagination_on_website = fields.Integer(
        related='website_id.request_pagination_on_website',
        readonly=False,
        required=True
    )
    request_quick_filters_on_website = fields.Boolean(
        related='website_id.request_quick_filters_on_website',
        readonly=False,
        required=True
    )
    request_use_time_in_datetime_on_website = fields.Boolean(
        related='website_id.request_use_time_in_datetime_on_website',
        readonly=False,
    )

    request_contained_on_website = fields.Boolean(
        config_parameter='crnd_vsd.request_contained_on_website',
        readonly=False,
        related='website_id.request_contained_on_website',
    )

    request_mail_link_access = fields.Selection(
        related='company_id.request_mail_link_access',
        readonly=False,
        string='Choose what kind of link to request will be used in emails.')

    # LIST VIEW
    request_list_column_assignee = fields.Boolean(
        config_parameter='crnd_vsd.request_list_column_assignee',
        readonly=False,
        related='website_id.request_list_column_assignee',
    )
    request_list_column_created_by = fields.Boolean(
        config_parameter='crnd_vsd.request_list_column_created_by',
        readonly=False,
        related='website_id.request_list_column_created_by',
    )

    # TODO: Delete this field after all clients migrated on 28.0 versions
    request_read_block_subrequests = fields.Boolean(
        config_parameter='crnd_vsd.request_read_block_subrequests',
        readonly=False,
        related='website_id.request_read_block_subrequests',
    )
    # TODO: Delete this field after all clients migrated on 28.0 versions
    request_read_block_comments = fields.Boolean(
        config_parameter='crnd_vsd.request_read_block_comments',
        readonly=False,
        related='website_id.request_read_block_comments',
    )

    request_use_custom_template = fields.Boolean(
        config_parameter='crnd_vsd.request_use_custom_template',
        readonly=False,
        related='website_id.request_use_custom_template')

    def set_values(self):
        # pylint: disable=missing-return
        super().set_values()
        if self.request_use_custom_template:
            default_template = self.env["ir.qweb"]._get_template(
                'crnd_vsd.requests_create_global_template')
            default_template_el = default_template[0]

            default_template_el.attrib['name'] = \
                'Requests create template (Custom)'
            default_template_el.attrib['t-name'] = \
                'crnd_vsd.requests_create_global_custom_template'

            custom_template = self.env.ref(
                "crnd_vsd.requests_create_global_custom_template")
            if custom_template:
                custom_template.arch_db = etree.tostring(
                    default_template_el, encoding="unicode", pretty_print=True)
