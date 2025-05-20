/** @odoo-module **/
import { Component, useState, onWillStart, onWillDestroy, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "@crnd_vsd/js/components/common/CRNDInputWidget";
import { CRNDInputSelectWidget } from "@crnd_vsd/js/components/common/CRNDInputSelectWidget/CRNDInputSelectWidget";


export class CRNDInputResourceWidget extends CRNDInputWidget {
  static template = 'crnd_vsd.CRNDInputResourceWidget'
  static components = {
    CRNDInputSelectWidget,
  }

  setup() {
    this.rpc = useService("rpc");
    this.state = useState({
      resourceType: {
        resources: [],
      },
      currentResource: null,
    })

    this.setCurrentResource = this.setCurrentResource.bind(this)

    onWillStart(async () => {
      await this.getResourceType();
    })

    this.updateInputValue()
  }

  setCurrentResource(key, value) {
    this.state.currentResource = value
    this.updateInputValue()
  }

  updateInputValue() {
    this.props._updateInputValue(this.props.name, this.state.currentResource);
  }

  async getResourceType() {
    if (this.props.resource_type_id) {
        const resourceType = await this.rpc(`/api/get_resource_type/${this.props.resource_type_id}`, {})
        if (resourceType) {
          this.state.resourceType = resourceType
        }
    }
  }

  getResourceList() {
    return this.state.resourceType?.resources?.map(item => ({
      value: item.id,
      name: item.name
    }))
  }

}
