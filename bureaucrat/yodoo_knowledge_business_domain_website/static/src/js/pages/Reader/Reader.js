/** @odoo-module **/
import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { Reader } from "@yodoo_knowledge_website/js/pages/Reader/Reader";
import { startParam } from "@yodoo_knowledge_website/js/features/startParam";



patch(Reader, {
    components: {
        ...Reader.components,
    },
})

patch(Reader.prototype, {
    setup() {
        super.setup();
        this.state.business_domains = [];
        this.state.selected_business_domain = null;

        this.setBusinessDomainId = this.setBusinessDomainId.bind(this)


        onWillStart(async () => {
            await this.getAvailableBusinessDomain();
        })
    },

    async getAvailableBusinessDomain() {
        const response = await this.rpc(
            '/yodoo_knowledge_business_domain_website/api/get_available_business_domains',
            {}
        );
        this.state.business_domains = response

        if (!this.item_id) {
            this.state.selected_business_domain = this.state.business_domains[0].id
            await this.getCategories()
            const firstItem = this.findFirstItem(this.state.categories)
            if (firstItem) {
                this.item_id = firstItem.id
                await this.getKnowledgeItem(this.item_id)
            }
        } else {
            await this.getKnowledgeItem(this.item_id)
            const currentBusinessDomain = this.state.business_domains.find(x => x.id == this.state.knowledgeItem?.business_domain_id)
            this.state.selected_business_domain = currentBusinessDomain?.id
            await this.getCategories()
        }
    },

    async setBusinessDomainId(value) {
        this.state.selected_business_domain = value
        await this.getCategories()
        
        // or first item in category OR default
        const firstItem = this.findFirstItem(this.state.categories)
        if (firstItem) {
            this.item_id = firstItem.id
            this.getKnowledgeItem(this.item_id)
        }

    },

    findFirstItem(categories) {
        for (const category of categories) {
            if (category.child) {
                if (category.child.items && category.child.items.length > 0) {
                    return category.child.items[0];
                }
                if (category.child.categories && category.child.categories.length > 0) {
                    const foundItem = this.findFirstItem(category.child.categories);
                    if (foundItem) {
                        return foundItem;
                    }
                }
            }
        }
        return null; 
    },

    getDataForCategoriesRequest() {
        const data = super.getDataForCategoriesRequest()
        data.business_domain_id = this.state.selected_business_domain
        return data
    },
});
