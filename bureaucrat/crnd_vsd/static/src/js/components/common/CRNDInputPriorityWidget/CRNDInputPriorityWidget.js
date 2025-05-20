/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "../CRNDInputWidget";


export class CRNDInputPriorityWidget extends CRNDInputWidget {
  static template = 'crnd_vsd.CRNDInputPriorityWidget'

  setup() {
    this.state = useState({
      priority: +this.props.default_value || +this.props._form_value || 3,
    })

    this.props._updateInputValue(this.props.name, this.state.priority)
  }
  
  getStarStatus(i) {
    return i <= this.state.priority
  }

  starClick(i) {
    this.state.priority = i
    this.props._updateInputValue(this.props.name, this.state.priority)
  }
}