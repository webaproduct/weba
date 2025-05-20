/** @odoo-module **/
import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "../CRNDInputWidget";


export class CRNDInputTextWidget extends CRNDInputWidget {
  static template = 'crnd_vsd.CRNDInputTextWidget'
  static defaultProps = {
    maxLength: 150,
  };

  setup() {
    this.state = useState({
        showLengthError: false,
        value: this.props._form_value || this.props.default_value || null,
    })

    onWillUpdateProps(nextProps => {
        this.updateInputValue(nextProps.default_value || nextProps._form_value || null)
    });

    this.props._updateInputValue(this.props.name, this.props.default_value || this.props._form_value || '')
  }

  onInputText(event) {
    const text = event.target.value;
    if (text.length > this.props.maxLength) {
        this.state.showLengthError = true
        event.preventDefault()
    } else {
        this.state.showLengthError = false
    }
  }

  updateInputValue(text) {
    this.state.showLengthError = false;

    if (text?.length > this.props.maxLength-1) {
        this.state.showLengthError = true;
        text = text?.substring(0, this.props.maxLength); // обрезаем текст
    }

    this.state.value = text
    this.props._updateInputValue(this.props.name, this.state.value)
  }

}