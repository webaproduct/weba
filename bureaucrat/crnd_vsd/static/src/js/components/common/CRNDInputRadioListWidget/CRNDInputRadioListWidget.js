/** @odoo-module **/
import { Component, useState, onWillStart, onWillDestroy, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "@crnd_vsd/js/components/common/CRNDInputWidget";


export class CRNDInputRadioListWidget extends CRNDInputWidget {
  static template = 'crnd_vsd.CRNDInputRadioListWidget'

  static getPropsFromXml(fieldElement) {
    // <field name="select_any" widget="CRNDInputSelectWidget" required="true" default_value="3" title="Priority">
    //     <option value="1" name="First option"/>
    //     <option value="2" name="Second option"/>
    //     <option value="3" name="Third option"/>
    // </field>

    const data = {
      selectList: [],
    }

    const optionList = fieldElement.querySelectorAll('option')

    for (let i = 0; i < optionList.length; i++) {
      const option = optionList[i]
      let value = option.getAttribute('value')

      if (+value) {
        value = +value
      }

      data.selectList.push({
        value: value,
        name: option.getAttribute('name'),
      })
    }
    return data
  }

  setup() {
    this.state = useState({
      items: [],
      active: false,
    })

    if (this.props.selectList) {
      this.state.items = this.props.selectList
    }
    if (this.props.default_value) {
      let value = this.props.default_value
      if (+value) {
        value = +value
      }

      const default_value = this.state.items.find(x => x.value == value)
      if (default_value) {
        this.state.active = default_value
      }
    }

    this.updateInputValue()
  }

  updateInputValue() {
    this.props._updateInputValue(this.props.name, this.state.active.value);
  }

  isActive(item) {
    return this.state.active?.value == item.value
  }

  onClickOption(item_obj) {
    this.state.active = item_obj
    this.updateInputValue();
  }
}