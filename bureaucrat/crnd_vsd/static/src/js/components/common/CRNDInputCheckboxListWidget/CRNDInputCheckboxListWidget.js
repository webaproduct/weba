/** @odoo-module **/
import { Component, useState, onWillStart, onWillDestroy, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "@crnd_vsd/js/components/common/CRNDInputWidget";


export class CRNDInputCheckboxListWidget extends CRNDInputWidget {
  static template = 'crnd_vsd.CRNDInputCheckboxListWidget'

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
      activeItems: [],
    })

    if (this.props.selectList) {
      this.state.items = this.props.selectList
    }
    if (this.props.default_value) {
      let valueList = []

      for (let value in this.props.default_value) {
        if (+value) {
          value = +value
        }
        valueList.push(value)
      }

      const default_value = this.state.items.filter(x => valueList.includes(x.value))
      if (default_value.length) {
        this.state.activeItems = default_value
      }
    }

    this.updateInputValue()
  }

  updateInputValue() {
    const activeValues = []
    this.state.activeItems.forEach((activeObj) => {
      activeValues.push(activeObj.value)
    })
    this.props._updateInputValue(this.props.name, activeValues);
  }

  isActive(item) {
    const active_item = this.state.activeItems.find(x => x.value == item.value)
    return Boolean(active_item)
  }

  onClickOption(itemObj) {
    const activeItem = this.state.activeItems.find(x => x.value == itemObj.value)
    if (activeItem) {
      this.state.activeItems = this.state.activeItems.filter(x => x.value != activeItem.value)
    } else {
      this.state.activeItems.push(itemObj)
    }
    this.state.activeItems.item_obj
    this.updateInputValue();
  }
}
