
/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { KnowledgeNavigationCategory } from "./KnowledgeNavigationCategory/KnowledgeNavigationCategory";


export class KnowledgeNavigation extends Component {
    static template = "yodoo_knowledge_website.KnowledgeNavigation";
    static components = {
        KnowledgeNavigationCategory
    }
    static props = {
        categories: Array,
        setKnowledgeItem: Function,
    }
}