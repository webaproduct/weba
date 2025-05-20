/** @odoo-module **/
import { Component } from "@odoo/owl";


export class Pagination extends Component {
  static template = "crnd_vsd.Pagination";

    generatePaginationList(totalPages, currentPage) {
        if (totalPages < 1 || currentPage < 1 || currentPage > totalPages) {
            return [];
        }

        const startPage = Math.max(currentPage - 2, 1);
        const endPage = Math.min(currentPage + 2, totalPages);

        const paginationList = [];
        for (let i = startPage; i <= endPage; i++) {
            paginationList.push(i);
        }

        return paginationList;
    }
}
