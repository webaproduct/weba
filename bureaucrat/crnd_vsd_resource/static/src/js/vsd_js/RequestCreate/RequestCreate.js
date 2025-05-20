/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { RequestCreate } from "@crnd_vsd/js/components/MainContent/RequestCreate/RequestCreate";
import { CRNDInputResourceWidget } from "@crnd_vsd_resource/js/vsd_js/common/CRNDInputResourceWidget/CRNDInputResourceWidget";


patch(RequestCreate.prototype, {
    getComponents() {
        return {
            ...super.getComponents(),
            CRNDInputResourceWidget,
        }
    },
});
