
/** @odoo-module **/
import { Component, useState, onWillDestroy, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { startParam } from "../../features/startParam";


export class SearchField extends Component {
    static template = "yodoo_knowledge_website.SearchField";

    setup() {
        this.rpc = useService("rpc");
        this.website_id = startParam.website_id;
         
        this.state = useState({
            activeTab: null, // search
            searchText: null,
            searchTimioutId: null,
            knowledgeItems: [],
            isLoadingKnowledgeItems: false,
                    })

        // this.getKnowledgeItem = this.getKnowledgeItem.bind(this)
        useExternalListener(window, "click", this.clickOutside.bind(this), { capture: true });

        onWillDestroy(() => {
            window.removeEventListener("click", this.clickOutside.bind(this), { capture: true })
        })
    }

    clickOutside() {
        const element = document.getElementById('yodoo_knowledge_website_search_field')
        if (!element) {
            return;
        }

        const isClickInside = element.contains(event.target)
        if (!isClickInside) {
            this.closeAllMenu();
        }
    }

    closeAllMenu() {
        this.state.activeTab = null;
    }

    clickOnKnowledgeItem(item_id) {
        this.closeAllMenu()
        this.props.setKnowledgeItem(item_id)
    }

    async fetchKnowledgeItems() {
        if (this.state.searchText) {
            const response = await this.rpc(
                '/yodoo_knowledge_website/api/search_knowledge_items', 
                {search_text: this.state.searchText}
            )
            this.state.knowledgeItems = response
        } else {
            this.state.knowledgeItems = []
        }
        this.state.isLoadingKnowledgeItems = false
    }

    async onInputSearch(e) {
        this.state.isLoadingKnowledgeItems = true
        this.state.activeTab = 'search';
        this.state.searchText = e.target.value;
        clearTimeout(this.state.searchTimioutId); 
        this.state.searchTimioutId = setTimeout(this.fetchKnowledgeItems.bind(this), 1000); 
    }
}