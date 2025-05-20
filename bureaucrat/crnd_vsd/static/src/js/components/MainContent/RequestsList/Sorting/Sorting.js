/** @odoo-module **/
import { Component, useState, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";


export class Sorting extends Component {
  static template = "crnd_vsd.Sorting";
  static props = {
    'setSortingItem': {
      type: Function,
    },
    'activeObj': {
      type: Object
    },
  }

  sortingItems = [
    {displayText: _t("Without sorting"), value: null},
    {displayText: _t("Newest"), value: "id DESC"},
    {displayText: _t("Oldest"), value: "id"},
    {displayText: _t("Name (A->Z)"), value: "name"},
    {displayText: _t("Name (Z->A)"), value: "name DESC"},
  ]
  
  setup() {
    this.rpc = useService("rpc");
    this.state = useState({
      isOpen: false
    })

    useExternalListener(window, "click", this.closeSortingList.bind(this), { capture: true });
  }

  openSortingList() {
    this.state.isOpen = true
  }
  closeSortingList(event) {
    const element = document.getElementById('crnd_sorting_block')
    if (!element) {
      return;
    }

    const isClickInside = element.contains(event.target)
    if (!isClickInside) {
      this.state.isOpen = false;
    }  
  }
  toogleSortingList() {
    this.state.isOpen = !this.state.isOpen
  }


  onClickSortingItem(item) {
    this.props.setSortingItem(item);
    this.state.isOpen = false
  }

  getSortingItems() {
    return this.sortingItems.filter(x => x.value != this.props.activeObj.value)
  }
}