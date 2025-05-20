import logging

from odoo import models, fields, api, exceptions, _
from odoo.addons.generic_mixin import post_create, post_write
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m

_logger = logging.getLogger(__name__)


class RequestClassifier(models.Model):
    _name = 'request.classifier'
    _inherit = [
        'generic.mixin.track.changes',
    ]
    _description = 'Request Classifier'
    _order = 'service_id ASC, category_id ASC, type_id ASC'

    service_id = fields.Many2one(
        'generic.service', string='Service', index=True, ondelete='restrict',
        help="Service of request")
    service_id_group = fields.Many2one(
        comodel_name='generic.service.group',
        related='service_id.service_group_id',
        string='Service group', store=True, readonly=True)
    category_id = fields.Many2one(
        'request.category', 'Category', index=True, ondelete="restrict",
        help="Category of request")
    type_id = fields.Many2one(
        'request.type', 'Type', index=True, ondelete='cascade', required=True,
        help="Type of request")
    kind_id = fields.Many2one(
        'request.kind', 'Kind', store=True, index=True, readonly=True,
        related='type_id.kind_id',
        help='Kind of request',
    )
    request_ids = fields.One2many(
        comodel_name='request.request',
        inverse_name='classifier_id')
    request_ids_count = fields.Integer(
        compute='_compute_request_ids_count')

    active = fields.Boolean(index=True, default=True)

    default_priority_request_title = fields.Char(translate=True)
    default_priority_request_text = fields.Html(translate=True)

    # Mail rules
    send_mail_on_request_created_event = fields.Boolean(
        default=True)
    request_created_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        default=lambda self: self._default_request_created_mail_template_id(),
        domain=[('model', '=', 'request.request')],
        help='This template will be used to send an email '
             'to the user when a new request is created.')
    send_mail_on_request_assigned_event = fields.Boolean(
        default=True)
    request_assigned_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        default=lambda self: self._default_request_assigned_mail_template_id(),
        domain=[('model', '=', 'request.request')],
        help='This template will be used to send an email '
             'to the user when a request is assigned.')
    send_mail_on_request_closed_event = fields.Boolean(
        default=True)
    request_closed_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        domain=[('model', '=', 'request.request')],
        default=lambda self: self._default_request_closed_mail_template_id(),
        help='This template will be used to send an email '
             'to the user when a request is closed.')
    send_mail_on_request_reopened_event = fields.Boolean(
        default=True)
    request_reopened_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        domain=[('model', '=', 'request.request')],
        default=lambda self: self._default_request_reopened_mail_template_id(),
        help='This template will be used to send an email '
             'to the user when a request is closed.')
    tag_category_ids = fields.Many2many(
        'generic.tag.category', 'request_classifier_tag_category_rel',
        'classifier_id', 'category_id', string='Tag Categories',
        domain=[('model_id.model', '=', 'request.request')],
        help='Restrict available tags for requests of this classifier '
             'by tags of these categories')

    # Computed field to enforce uniqueness across
    # service_id, category_id, and type_id.
    # This field addresses a limitation with SQL UNIQUE constraints:
    # NULL values are treated as unique, so the unique constraint
    # does not work when any of the fields are NULL.
    # The field concatenates IDs or uses '0' as a placeholder for NULL values
    # to achieve consistent unique values across these fields.
    unique_combination_key = fields.Char(
        compute='_compute_unique_combination_key',
        store=True
    )

    _sql_constraints = [
        ('unique_combination_key_unique',
         'UNIQUE(unique_combination_key)',
         "Binding: The combination of service_id, "
         "category_id, and type_id must be unique!")
    ]

    @api.depends('service_id', 'category_id', 'type_id')
    def _compute_unique_combination_key(self):
        for record in self:
            service = record.service_id.id if record.service_id else '0'
            category = record.category_id.id if record.category_id else '0'
            type_ = record.type_id.id if record.type_id else '0'
            record.unique_combination_key = f"{service}-{category}-{type_}"

    @api.depends('request_ids')
    def _compute_request_ids_count(self):
        mapped_data = read_counts_for_o2m(
            records=self,
            field_name='request_ids', sudo=True)
        for record in self:
            record.request_ids_count = mapped_data.get(record.id, 0)

    @api.model
    def get_classifiers(self, service=None, category=None,
                        request_type=None, limit=None):
        """ Return classifier recordset with mentioned service, category, type.
        """
        def get_id(value):
            if isinstance(value, str):
                return self.env.ref(value).id
            if isinstance(value, models.BaseModel):
                return value.id
            if isinstance(value, int):
                return value
            if value is None or value is False:
                return value
            raise AssertionError("Unknown format: %s" % value)

        service_id = get_id(service)
        category_id = get_id(category)
        type_id = get_id(request_type)

        domain = []
        if service_id is not None:
            domain.append(('service_id', '=', service_id))
        if category_id is not None:
            domain.append(('category_id', '=', category_id))
        if type_id is not None:
            domain.append(('type_id', '=', type_id))

        classifier = self.env['request.classifier'].search(domain, limit=limit)
        return classifier

    @api.model
    def _default_request_created_mail_template_id(self):
        template = self.env.ref(
            'generic_request.mail_template_default_request_create',
            raise_if_not_found=False)
        return template.id if template else None

    @api.model
    def _default_request_assigned_mail_template_id(self):
        template = self.env.ref(
            'generic_request.mail_template_default_request_assign',
            raise_if_not_found=False)
        return template.id if template else None

    @api.model
    def _default_request_closed_mail_template_id(self):
        template = self.env.ref(
            'generic_request.mail_template_default_request_closed',
            raise_if_not_found=False)
        return template.id if template else None

    @api.model
    def _default_request_reopened_mail_template_id(self):
        template = self.env.ref(
            'generic_request.mail_template_default_request_reopened',
            raise_if_not_found=False)
        return template.id if template else None

    @api.depends('display_name')
    def _compute_display_name(self):
        for record in self:
            if self.env.user.has_group(
                    'generic_request.group_request_use_services'):
                name = "%s - %s - %s" % (
                    record.service_id.name,
                    record.category_id.name,
                    record.type_id.name)
            else:
                name = "%s - %s" % (
                    record.category_id.name,
                    record.type_id.name)
            record.display_name = name
        return True

    @post_create()
    @post_write('service_id', 'category_id', 'type_id', 'active')
    def _update_cache_for_m2m_relations_on_srv_categ_type(self, changes):
        self.env['request.type'].invalidate_model(
            fnames=['category_ids', 'service_ids'])
        if self.category_id:
            self.env['request.category'].invalidate_model(
                fnames=['request_type_ids', 'service_ids'])
        if self.service_id:
            self.env['generic.service'].invalidate_model(
                fnames=['request_type_ids', 'category_ids'])

    def unlink(self):
        services = self.mapped('service_id')
        categories = self.mapped('category_id')
        types = self.mapped('type_id')
        res = super().unlink()

        self.env['request.type'].browse(
            ids=types.ids).invalidate_recordset(
            fnames=['category_ids', 'service_ids'])

        if categories:
            self.env['request.category'].browse(
                ids=categories.ids).invalidate_recordset(
                fnames=['request_type_ids', 'service_ids'])
        if services:
            self.env['generic.service'].browse(
                ids=services.ids).invalidate_recordset(
                fnames=['request_type_ids', 'category_ids'])
        return res

    def action_show_related_requests(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_request.action_request_window',
            domain=[('classifier_id.id', '=', self.id)],
        )

    def write(self, values):
        # Avoid changing classifiers when classifier has related requests
        has_requests = self.mapped('request_ids')
        restricted_fields = {'service_id', 'category_id', 'type_id'}
        if restricted_fields.intersection(set(values)) and has_requests:
            _logger.warning(
                "Attempted to modify classifier %s "
                "with related request records.",
                self
            )
            raise exceptions.UserError(
                _('You can\'t change classifier '
                  'because related request records exist.'))

        return super().write(values)
