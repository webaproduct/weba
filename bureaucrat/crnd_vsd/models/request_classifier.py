from odoo import models, fields


class RequestClassifier(models.Model):
    _inherit = 'request.classifier'

    website_published = fields.Boolean(
        'Visible in Website', copy=False, index=True)
    website_ids = fields.Many2many(
        comodel_name='website',
        relation='request_classifier_website_rel',
        column1='request_classifier_id',
        column2='website_id')

    website_comments_closed = fields.Boolean(
        'Are comments not available?', default=False,
        help="Disable website comments on closed requests")

    # Help message for request text
    website_request_text_help = fields.Text()
    # Custom title for request
    website_request_title = fields.Char()
    # Custom label for request text editor
    website_custom_label_editor = fields.Char()
    website_custom_congratulation_note = fields.Html()

    # READ visibility rules
    read_show_priority = fields.Boolean(default=False)
    read_show_comments = fields.Boolean(default=False)
    read_show_subrequests = fields.Boolean(default=False)
    read_show_files = fields.Boolean(default=False)
    read_show_created_by = fields.Boolean(default=False)
    read_show_responsible = fields.Boolean(default=False)
    read_show_assignee = fields.Boolean(default=False)
    read_show_updated_by = fields.Boolean(default=False)
    read_show_closed_by = fields.Boolean(default=False)
    read_show_followers = fields.Boolean(default=False)

    # CREATE visibility rules
    create_show_title = fields.Boolean(default=True)
    create_show_text = fields.Boolean(default=True)
    create_show_priority = fields.Boolean(default=False)
    create_show_files = fields.Boolean(default=False)

    def website_publish_button(self):
        for rec in self:
            rec.website_published = not rec.website_published
        return True
