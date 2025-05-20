from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    use_service_groups = fields.Boolean(
        default=False)

    request_redirect_after_created_on_website = fields.Selection(
        selection=[('congrats_page', 'Redirect to congratulation page'),
                   ('req_page', 'Redirect to request page')],
        default='congrats_page',
        required=True
    )

    request_pagination_on_website = fields.Integer(
        default=20,
        required=True
    )
    request_quick_filters_on_website = fields.Boolean(
        default=True,
        required=True
    )
    request_use_time_in_datetime_on_website = fields.Boolean(
    )

    # LIST VIEW
    request_contained_on_website = fields.Boolean(
        default=True,
        required=True
    )

    request_list_column_assignee = fields.Boolean(
        default=True,
        required=True
    )
    request_list_column_created_by = fields.Boolean(
        default=True,
        required=True
    )

    # TODO: Delete this field after all clients migrated on 28.0 versions
    request_read_block_subrequests = fields.Boolean(
        default=True,
        required=True
    )
    # TODO: Delete this field after all clients migrated on 28.0 versions
    request_read_block_comments = fields.Boolean(
        default=True,
        required=True
    )

    request_use_custom_template = fields.Boolean(default=False)

    def get_request_public_ui(self):
        """ Get type of public UI for request
        """
        self.ensure_one()
        return self.company_id.request_wsd_public_ui_visibility

    def get_request_public_use_author_phone(self):
        """ Get for public UI use author phone for request
        """
        self.ensure_one()
        return self.company_id.request_wsd_public_use_author_phone

    def is_request_author_phone_required(self):
        self.ensure_one()
        if not self.is_public_user():
            return False
        if self.get_request_public_use_author_phone() == 'required-phone':
            return True
        return False

    def is_request_restricted_ui(self):
        """ Check if restricted UI set in configuration
        """
        self.ensure_one()
        if not self.is_public_user():
            return False
        if self.get_request_public_ui() == 'restrict':
            return True
        return False

    def is_request_create_public(self):
        """ Return True only if current user is public user and
            the system configured to allow public users to create requests
        """
        self.ensure_one()
        if not self.is_public_user():
            return False
        if self.get_request_public_ui() == 'create-request':
            return True
        return False
