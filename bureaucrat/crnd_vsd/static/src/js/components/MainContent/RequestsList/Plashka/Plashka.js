/** @odoo-module **/
import { Component } from "@odoo/owl";

import { PlashkaFilterList } from "./PlashkaFilterList/PlashkaFilterList";

export class Plashka extends Component {
  static template = "crnd_vsd.Plashka";
  static components = {
    PlashkaFilterList
  }

  getFiltersValues(values) {
    return values.join(", ")
  }

  getActiveCeavLength(active_ceav_filters) {
    return active_ceav_filters.filter((obj) => obj.values.length).length
  }
}
