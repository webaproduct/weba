
/** @odoo-module **/
import { Component, useState, markup, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { startParam } from "../../features/startParam";
import { 
    changeUrlWithoutRedirect,
    decodeDataBehaviorProps,
    updateMetaTag,
} from "../../features/utils";

import { KnowledgeNavigation } from "../../components/KnowledgeNavigation/KnowledgeNavigation";
import { KnowledgeItem } from "../../components/KnowledgeItem/KnowledgeItem";
import { Scrollspy } from "../../components/scrollspy/scrollspy";
import { SearchField } from "../../components/SearchField/SearchField";
import { FilterList } from "../../components/FilterList/FilterList";

export class Reader extends Component {
    static template = "yodoo_knowledge_website.Reader";
    static components = {
        KnowledgeNavigation,
        KnowledgeItem,
        Scrollspy,
        SearchField,
        FilterList,
    }


    setup() {
        this.rpc = useService("rpc");
        this.website_id = startParam.website_id;
        this.item_id = Number(startParam.item_id) || 1;

        this.state = useState({
            isLoadingItem: true,
            isLoadingCategories: true,
            categories:[],
            knowledgeItem: null,
            scrollspyItems: [],
            errors: {
                knowledgeItem: null,
            },

            isSidepanelOpen: false,

            filters: {},
            isOpenFilterList: false,

        })
        this.getKnowledgeItem = this.getKnowledgeItem.bind(this)
        this.saveFilterList = this.saveFilterList.bind(this)
        this.toggleFilterList = this.toggleFilterList.bind(this)

        onWillStart(async () => {
            await this.getCategories()
            await this.getKnowledgeItem(this.item_id)

            const scrollspyEl = document.querySelector('#wrapwrap');

            scrollspyEl.classList.add('scrollspy-content');
            scrollspyEl.setAttribute('data-bs-spy', 'scroll');
            scrollspyEl.setAttribute('data-bs-target', '#scrollspy-nav');
            scrollspyEl.setAttribute('data-bs-offset', '80');
            scrollspyEl.setAttribute('tabindex', '0');
        })
    }

    async saveFilterList(filter_data) {
        this.state.filters = filter_data;
        await this.getCategories()
    }

    getFilterDataCount() {
        return Object.values(this.state.filters).filter(x => x).length
    }

    async getCategories() {
        this.state.isLoadingCategories = true;
        const data = this.getDataForCategoriesRequest()
        
        const response = await this.rpc('/yodoo_knowledge_website/api/get_categories', data);
        this.state.categories = response
        this.state.isLoadingCategories = false;
    }
    getDataForCategoriesRequest() {
        const filter_data = [];
        Object.entries(this.state.filters).forEach(([key, value]) => {
            filter_data.push({"name": key, "value": value})
        });
        return {
            website_id: this.website_id,
            filters: filter_data
        }
    }



    async getKnowledgeItem(item_id) {
        this.state.isLoadingItem = true;
        this.closeSidepanel()
        
        const response = await this.rpc(
            '/yodoo_knowledge_website/api/get_knowledge_item',
            this.getDataForKnowledgeItemRequest(item_id),
        );
        if (!response) {
            this.state.errors.knowledgeItem = "Knowledge item was not found"
            return 
        }
        this.state.errors.knowledgeItem = null;
        this.state.knowledgeItem = response;
        if (this.state.knowledgeItem?.id) this.item_id = this.state.knowledgeItem?.id
        changeUrlWithoutRedirect(this.state.knowledgeItem.code, this.state.knowledgeItem.name);
        updateMetaTag("og:title", this.state.knowledgeItem.name);
        

        if (this.state.knowledgeItem.item_type == 'pdf') {
            updateMetaTag("og:description", "PDF file");
        } else {
            updateMetaTag("og:description", this.state.knowledgeItem.body);
            const [updatedItemBody, scrollspyItems] = this.prepareItemHtmlForScrollspy(response.body);
            this.state.knowledgeItem.body = markup(updatedItemBody);
            this.state.scrollspyItems = scrollspyItems;
        }

        this.state.isLoadingItem = false;

        this.state.knowledgeItem.parent_path = this.state.knowledgeItem.parent_path ? this.state.knowledgeItem.parent_path?.split('/') : [];    
    }
    getDataForKnowledgeItemRequest(item_id) {
        return {
            website_id: this.website_id,
            item_id: item_id,
        }
    }

    prepareItemHtmlForScrollspy(body) {
        if (!body) return ['', []];

        const idsForScrollspyNav = [];
        
        const parser = new DOMParser();
        const itemVirtualDOM = parser.parseFromString(body, 'text/html');
        const itemHeaders = itemVirtualDOM.querySelectorAll('h1,h2,h3,h4,h5');
        
        let counter = 0;
        itemHeaders.forEach(header => {
            let headerId = header.getAttribute('id');
            if (!headerId) {
                headerId = `scrollspy-header-${counter}`;
                counter++;
                header.setAttribute('id', headerId);
            }
            idsForScrollspyNav.push({
                headerId,
                text: header.innerText,
            }); 
        });

        const itemImgs = itemVirtualDOM.querySelectorAll('img');
        itemImgs.forEach((imgElement) => {
            imgElement.setAttribute('loading', 'lazy')
        })

        const wikiLinks = itemVirtualDOM.querySelectorAll('a.o_yodoo_knowledge_behavior_type_knowledge_item');
        wikiLinks.forEach((wikiLink) => {
            const data = decodeDataBehaviorProps(wikiLink.getAttribute('data-behavior-props')) 
            wikiLink.setAttribute('href', `/knowledge/item/${data.knowledgeItem_code}`)
        })

        const idsForScrollspyNavFiltered = idsForScrollspyNav.filter((headerConf) => headerConf.text);

        return [itemVirtualDOM.body.innerHTML, idsForScrollspyNavFiltered];
    }

    openSidepanel() {
        this.state.isSidepanelOpen = true
    }
    closeSidepanel() {
        this.state.isSidepanelOpen = false
    }

    toggleFilterList(status) {
        if (status === undefined) {
          this.state.isOpenFilterList = !this.state.isOpenFilterList
        } else {
          this.state.isOpenFilterList = status
        }
      }
}