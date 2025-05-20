/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FilterList } from "@crnd_vsd/js/components/MainContent/RequestsList/FilterList/FilterList";

patch(FilterList.prototype, {
    setup() {
        super.setup();
        this.state.tags = [];

        this.tagIconUrl = '/crnd_vsd_tag/static/img/tag.svg'
    },

    async getAdditionalData() {
        await super.getAdditionalData();
        await this.getTags();
    },

    async getTags() {
        const tags = await this.rpc('/api/get_tags', {
            website_id: this.website_id,
        });
        if (tags.length) {
            this.state.tags = tags;
        }
    },

    getTagsSelectList(tags) {
        return tags.map(item => ({
            value: item.id,
            name: item.name
        }));
    },

    getIconByKey(key) {
        if (key.includes('tag_')) {
            return this.tagIconUrl
        } else {
            return super.getIconByKey(key)
        }
    },
});
