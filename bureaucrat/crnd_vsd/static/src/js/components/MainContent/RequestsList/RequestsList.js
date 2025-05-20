/** @odoo-module **/
import { Component, useState, onWillStart, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

import { startParam } from "../../../features/startParam";

import { FilterList } from "./FilterList/FilterList.js";
import { RequestsListTable } from "./RequestsListTable/RequestsListTable.js";
import { RequestsListKanban } from "./RequestsListKanban/RequestsListKanban.js"; 
import { Pagination } from "../../common/Pagination/Pagination.js";
import { Sorting } from "./Sorting/Sorting.js";
import { Plashka } from "./Plashka/Plashka.js";
import { PlashkaFilterList } from "./Plashka/PlashkaFilterList/PlashkaFilterList.js";


export class RequestsList extends Component {
  static template = "crnd_vsd.RequestsList";
  static components = {
    FilterList,
    RequestsListTable,
    RequestsListKanban,
    Pagination,
    Sorting,
    Plashka,
    PlashkaFilterList,
  } 


    reqStatusList = [
        {
            value: 'my',
            name: _t('My request'),
        },
        {
            value: 'for_me',
            name: _t('For me'),
        },
        {
            value: 'all',
            name: _t('All'),
        },
        {
            value: 'open',
            name: _t('Open'),
        },
        {
            value: 'closed',
            name: _t('Closed'),
        },
    ]


  setup() {
    this.rpc = useService("rpc");
    this.website_id = startParam.website_id;
    this.use_quick_filters = startParam.use_quick_filters;
    this.state = useState({
      requests: [],
      reqStatus: 'all', // my, all, open, closed, for_me
      page: 1,
      viewMode: 'list', // kanban
      isOpenFilterList: false,
      filterData: {
        global_search: {
            value: null,
        }, 
      },
      sortingItem: {
        displayText: null,
        value: null,
      },
      updatePlashka: 0,
    })
    

    this.changePage = this.changePage.bind(this);
    this.toggleFilterList = this.toggleFilterList.bind(this);
    this.saveFilterList = this.saveFilterList.bind(this);
    this.changeRequestStatus = this.changeRequestStatus.bind(this);
    this.setSortingItem = this.setSortingItem.bind(this);
    this.deleteAllFilters = this.deleteAllFilters.bind(this);
    this.deleteFilter = this.deleteFilter.bind(this);
    this.deleteFilterValue = this.deleteFilterValue.bind(this);

    onWillStart(async () => {
      await this.getRequestsItems()
    })

    this.onWindowResize()
    useExternalListener(window, "resize", this.onWindowResize.bind(this));
  }

  onWindowResize() {
    if (document.body.clientWidth <= 768) {
        this.state.viewMode = 'kanban'
      }
  }

  getFilterDataCount() {
    return Object.values(this.state.filterData).filter(x => {
        if (Array.isArray(x)) return x.length
        // if (typeof x === 'object' && x !== null) return true
    }).length
  }

  async changeViewMode(viewMode) {
    this.state.viewMode = viewMode;
    this.state.page = 1;
    // await this.changeRequestStatus('all')
  }
  async changeRequestStatus(status) {
    this.state.reqStatus = status;
    this.state.page = 1;
    await this.getRequestsItems();
  }

  searchQueryInputEvent(event) {
    this.state.filterData.global_search.value = event.target.value;

    if (this.timeoutId) {
        clearTimeout(this.timeoutId);
    }
    this.timeoutId = setTimeout(() => {
        this.getRequestsItems();
    }, 1000);
  }


  async setSortingItem(sortingItem) {
    this.state.sortingItem = sortingItem;
    await this.getRequestsItems();
  }

  onClickCreate() {
    window.location.href = "/requests/create";
  }

  async saveFilterList(filter_data) {
    // if ('global_search' in filter_data) {
    //     delete filter_data['global_search']
    // }
    this.state.filterData = {
        ...this.state.filterData,
        ...filter_data,
    };
    this.state.page = 1;
    await this.getRequestsItems()
  }

  async deleteFilterValue(key, value) {
    const filValObj = this.state.filterData[key].value
    if (Array.isArray(filValObj)) {
        this.state.filterData[key].value = this.state.filterData[key].value.filter(x => x.value != value)
        if (!this.state.filterData[key].value.length) {
            await this.deleteFilter(key)
            return
        }
    }
    await this.getRequestsItems()
    this.state.updatePlashka += 1
  }

  async deleteFilter(key) {
    delete this.state.filterData[key]
    this.state.updatePlashka += 1
    await this.getRequestsItems()
  }

  async deleteAllFilters() {
    this.state.filterData = {
        global_search: {
            value: null,
        },
    }
    await this.getRequestsItems()
    this.state.updatePlashka += 1
  }

  toggleFilterList(status) {
    if (status === undefined) {
      this.state.isOpenFilterList = !this.state.isOpenFilterList
    } else {
      this.state.isOpenFilterList = status
    }
  }

  changePage(page) {
    this.state.page = page;
    this.getRequestsItems();
  }

  async getRequestsItems() {
    const filter_data = [];
    Object.entries(this.state.filterData).forEach(([key, value_obj]) => {   
        const value = key == 'global_search' ? value_obj?.value : value_obj?.value?.map(x => x?.value)
      filter_data.push({"name": key, "value": value})
    });
    this.state.requests = await this.rpc('/api/get_requests', {
      website_id: this.website_id,
      req_status: this.state.reqStatus,
      page: this.state.page,
      filter_list: filter_data,
      sorting: this.state.sortingItem?.value,
    })
  }
}