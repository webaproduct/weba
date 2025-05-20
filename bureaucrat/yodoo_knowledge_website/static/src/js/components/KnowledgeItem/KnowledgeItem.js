/** @odoo-module **/

import { Component, onPatched, onMounted } from '@odoo/owl'

export class KnowledgeItem extends Component {
    static template = "yodoo_knowledge_website.KnowledgeItem";
    static props = {
        item: Object,
    }

    setup() {
        onMounted(() => {
            this.dataSpyEl = document.querySelector('#wrapwrap');;
            this.scrollspyInstance = ScrollSpy.getOrCreateInstance(this.dataSpyEl);

            this.initOrRefreshScrollspyInstances()

            const url = new URL(window.location.href)
            if (url.hash) {
                location.hash = ''
                location.hash = url.hash
            }
        })

        onPatched(() => {
            this.scrollspyInstance = ScrollSpy.getOrCreateInstance(this.dataSpyEl);

            this.initOrRefreshScrollspyInstances();
        })
    }

    initOrRefreshScrollspyInstances() {
        this.dataSpyEl.scrollTo({ top: 0, behavior: 'smooth' });
        const docImgs = this.dataSpyEl.querySelectorAll('img');
        let imageCount = 0;
        let totalImgAmount = docImgs.length;

        const loadedImgHandler = () => {
            imageCount++;
            
            if (imageCount === totalImgAmount) {
                this.scrollspyInstance.refresh();
            }
        }

        const loadImgErrorHandler = () => {
            totalImgAmount--;
        }

        docImgs.forEach((imgElement) => {
            imgElement.addEventListener('load', loadedImgHandler);
            imgElement.addEventListener('error', loadImgErrorHandler);
        })
    }
}
