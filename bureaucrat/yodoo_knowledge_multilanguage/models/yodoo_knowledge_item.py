from odoo import models, fields, api
from odoo.addons.generic_mixin import post_write


ENGLISH_LANG_ID = 1


class YodooKnowledgeItem(models.Model):
    _inherit = 'yodoo.knowledge.item'

    item_body_html = fields.Html(
        compute='_compute_item_body_html',
        readonly=False,
    )
    language_id = fields.Many2one(
        'res.lang',
        string="Language",
        compute="_compute_language_id",
        readonly=False,
        store=True
    )

    @api.depends('history_ids')
    def _compute_language_id(self):
        for record in self:
            last_version = record.history_ids.sorted(
                "create_date", reverse=True)[:1]
            record.language_id = last_version.language_id \
                if last_version else self.env.ref("base.lang_en")

    def _get_history_item_by_lang(self, lang_id: int):
        self.ensure_one()
        last_version = self.history_ids.filtered(
            lambda x: x.language_id and x.language_id.id == lang_id
        ).sorted("create_date", reverse=True)

        if last_version:
            last_version = last_version[0]

        return last_version

    def _get_action_view_history_context(self):
        context = super()._get_action_view_history_context()
        context['searchpanel_default_language_id'] = self.language_id.id
        return context

    @api.depends('language_id')
    def _compute_item_body_html(self):
        for record in self:
            latest_history = record._get_history_item_by_lang(
                self.language_id.id)

            if latest_history:
                record.item_body_html = latest_history[0].item_body_html
            else:
                record.item_body_html = False

    def _get_history_save_data(self, item):
        data = super()._get_history_save_data(item)
        data['language_id'] = item.language_id.id
        return data

    @post_write(
        'name',
        'item_format',
        'item_body_html',
        'item_body_pdf')
    def _post_item_changed(self, changes):
        last_version = self._get_history_item_by_lang(self.language_id)
        if last_version:
            if (changes.get('item_body_html').new_val
                    != last_version.item_body_html):
                self._save_item_history()
        else:
            self._save_item_history()
