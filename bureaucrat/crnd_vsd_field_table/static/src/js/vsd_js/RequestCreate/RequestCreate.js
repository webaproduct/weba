/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { RequestCreate } from "@crnd_vsd/js/components/MainContent/RequestCreate/RequestCreate";
import { CRNDFieldTableWidget } from "@crnd_vsd_field_table/js/vsd_js/common/CRNDFieldTableWidget/CRNDFieldTableWidget";


patch(RequestCreate.prototype, {
    getComponents() {
        return {
            ...super.getComponents(),
            CRNDFieldTableWidget,
        }
    },
});
