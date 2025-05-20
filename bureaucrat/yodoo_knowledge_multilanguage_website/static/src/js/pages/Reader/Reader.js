/** @odoo-module **/
import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { Reader } from "@yodoo_knowledge_website/js/pages/Reader/Reader";
import { YodooInputSelectWidget } from "@yodoo_knowledge_website/js/components/common/YodooInputSelectWidget/YodooInputSelectWidget";


patch(Reader, {
    components: {
        ...Reader.components,
        YodooInputSelectWidget
    },
})

patch(Reader.prototype, {
    setup() {
        super.setup();
        this.state.languages = [];
        this.state.selected_language_id = null; 

        this.setLanguageId = this.setLanguageId.bind(this)


        onWillStart(async () => {
            await this.getAvailableLanguages();
        })
    },

    async getAvailableLanguages() {
        const response = await this.rpc(
            '/yodoo_knowledge_multilanguage_website/api/get_available_languages',
            {}
        );
        this.state.languages = response?.map(item => ({
            value: item.id,
            name: item.name
        }));

        const cookieLangCode = this._getCookie('frontend_lang')
        if (cookieLangCode) {
            const cookieLang = response.find(x => x.code == cookieLangCode)
            if (cookieLang) {
                this.setLanguageId(cookieLang.id)
                return
            }
        }
        
        this.setLanguageId(this.state.languages[0].value);
    },

    _getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    },
    
    setLanguageId(value) {
        this.state.selected_language_id = value
        this.getCategories()
        this.getKnowledgeItem(this.item_id)
    },

    getDataForCategoriesRequest() {
        const data = super.getDataForCategoriesRequest()
        data.language_id = this.state.selected_language_id
        return data
    },

    getDataForKnowledgeItemRequest(item_id) {
        const data = super.getDataForKnowledgeItemRequest(item_id)
        data.language_id = this.state.selected_language_id
        return data
    }

});
