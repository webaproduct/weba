/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";

export class Scrollspy extends Component {
    static template = "yodoo_knowledge_website.scrollspy";
    static props = {
        scrollspyItems: Array
    }
}
