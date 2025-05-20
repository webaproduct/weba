
/** @odoo-module **/
import { Component, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


export class KnowledgeNavigationCategory extends Component {
    static template = "yodoo_knowledge_website.KnowledgeNavigationCategory";
    static components = {
        KnowledgeNavigationCategory
    }

    static props = {
        category: Object,
        setKnowledgeItem: Function,
    }
    itemRef = useRef('itemRef');

    // category structure
    // {
    //     id: category.id,
    //     name: category.name,
    //     child: {
    //         categories: [],
    //         items: []
    //     },
    //     parent_id: category.parent_id.id,
    // }

    onItemClick(item_id) {
        this.props.setKnowledgeItem(item_id)
    }

    toggleExpand() {
        this.itemRef.el.classList.toggle('expanded');
    }

}