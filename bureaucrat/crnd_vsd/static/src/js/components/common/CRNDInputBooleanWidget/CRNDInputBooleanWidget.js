/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "../CRNDInputWidget";


export class CRNDInputBooleanWidget extends CRNDInputWidget {
  static template = 'crnd_vsd.CRNDInputBooleanWidget'

  setup() {
    this.state = useState({
      boolean: !!this.props.default_value || !!this.props._form_value || false
    })

    this.props._updateInputValue(this.props.name, this.state.boolean)
  }

  updateInputValue(event) {
    this.state.boolean = !!event.target.checked;
    this.props._updateInputValue(this.props.name, this.state.boolean)
  }

}

CRNDInputBooleanWidget.props = {
  ...CRNDInputBooleanWidget,
  'title': {
    type: String,
    optional: false,
  },
}