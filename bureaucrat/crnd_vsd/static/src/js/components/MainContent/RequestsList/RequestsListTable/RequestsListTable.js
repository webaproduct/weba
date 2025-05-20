/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { RequestListTableItem } from "./RequestListTableItem/RequestListTableItem";

export class RequestsListTable extends Component {
  static template = "crnd_vsd.RequestsListTable";
  static components = {
    RequestListTableItem
  }

  // sortingItems = {
  //   "id": "",
  //   "name": "",
  //   "created_date": "",
  //   "stage": "",
  // }

  setup() {
    this.rpc = useService("rpc");
    this.state = useState({
      allowedColumns: []
    })

    this.isAllowed = this.isAllowed.bind(this)
    
    onWillStart(async () => {
      await this.getAllowedColumns()
    })
  }

  async getAllowedColumns() {
    const response = await this.rpc('/api/get_allowed_table_columns', {})
    this.state.allowedColumns = response
  }

  getClassStatusSorting(value) {
    // 3 statuses
    if (!this.props.sortingItem?.value) {
      return 'sorting_table_non_active'
    } else if (this.props.sortingItem?.value == value) {
      return 'sorting_table_active'
    } else if (this.props.sortingItem?.value.includes(value)) {
      return 'sorting_table_active_desc' 
    }
    return 'sorting_table_non_active'
  }

  clickOnSortingItem(value) {
    let sortValue = value
    if (this.props.sortingItem?.value == value) {
      sortValue = value + " DESC"
    }
    this.props.setSortingItem({
      displayText: sortValue, 
      value: sortValue,
    })
  }

  isAllowed(name) {
    return this.state.allowedColumns.includes(name)
  }
}