/** @odoo-module **/
import { Component, useState, onWillStart, onWillUpdateProps, onWillDestroy, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "../CRNDInputWidget";


export class CRNDInputSelectWidget extends CRNDInputWidget {
  static template = 'crnd_vsd.CRNDInputSelectWidget'

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
      isOpen: false,
      items: [],
      active: false,
      find_text: ''
    })

    this.updateItemsFromProps(this.props)

    onWillUpdateProps(nextProps => {
      this.updateItemsFromProps(nextProps)
    });
    

    useExternalListener(window, "click", this.closeMenu.bind(this), { capture: true });

    onWillDestroy(() => {
      window.removeEventListener("click", this.closeMenu.bind(this), { capture: true })
    })

    this.updateInputValue()
  }

  updateItemsFromProps(props) {
    if (props.selectList) {
      this.state.items = props.selectList
    }

    if ( !props.forceUpdateValue ) {
        if (!(props.default_value || props._form_value)) {
            return
        }
    }

    let value = props.default_value || props._form_value
    if (+value) {
        value = +value
    }

    const default_value = this.state.items.find(x => x.value == value)
    if (default_value) {
        this.state.active = default_value
    } else {
        if (props.forceUpdateValue) {
            this.state.active = false
        }
    }
  }

  updateInputValue() {
    this.props._updateInputValue(
        this.props.name, 
        this.state.active.value, 
        {
            value: this.state.active.value,
            name: this.state.active.name,
        }
    );
  }


  isActive(item) {
    return this.state.active?.value == item.value
  }

  isSorted(item) {
    if (this.state.find_text) {
      const regex = new RegExp(this.state.find_text, "i");
      return regex.test(item.name)
    }
    return true
  }

  onClickOption(item_obj) {
    this.state.isOpen = false;
    this.state.active = item_obj
    this.updateInputValue();
  }

  onClickSelect() {
    if (this.state.items.length > 0) {
      this.state.isOpen = !this.state.isOpen;
    }
  }

  closeMenu(event) {
    const element = document.getElementById('crnd_widget_' + this.props.name)
    if (!element) {
      return;
    }

    const isClickInside = element.contains(event.target)
    if (!isClickInside) {
      this.state.isOpen = false;
    }
  }
}

CRNDInputSelectWidget.props = {
  ...CRNDInputSelectWidget,
  "selectList": {
    type: Array,
    optional: false,
  },
  "is_find": {
    type: Boolean,
    optional: true,
  },
  
}