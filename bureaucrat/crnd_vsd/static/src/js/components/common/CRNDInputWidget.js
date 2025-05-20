/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


export class CRNDInputWidget extends Component {
  static props = {
    '_updateInputValue': {
      type: Function,
    },
    'name': {
      type: String
    },
    'title': {
      type: String,
      optional: true,
    },
    'required': {
      type: Boolean,
    },
    'placeholder': {
      type: String,
      optional: true,
    },
    'default_value': {
      optional: true,
    },
    'disabled': {
      optional: true,
    }
  }

  static getPropsFromXml(fieldElement) {
    return {}
  }
  static beforeDelete() {
  }
}