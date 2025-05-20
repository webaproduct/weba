/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "../CRNDInputWidget";


export class CRNDInputIntegerWidget extends CRNDInputWidget {
  static template = 'crnd_vsd.CRNDInputIntegerWidget'

  setup() {
    this.state = useState({
      number: +this.props.default_value || this.props._form_value || null
    })

    this.props._updateInputValue(this.props.name, this.state.number)
  }

  updateInputValue(event) {
    this.state.number = +event.target.value;
    this.props._updateInputValue(this.props.name, this.state.number)
  }

}