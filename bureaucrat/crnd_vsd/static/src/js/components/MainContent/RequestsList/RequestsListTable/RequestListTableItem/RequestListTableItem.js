/** @odoo-module **/
import { Component } from "@odoo/owl";
import { redirectToReqView } from "../../../../../features/utils";

export class RequestListTableItem extends Component {
  static template = "crnd_vsd.RequestListTableItem";

  clickOnReqName(req_id) {
    redirectToReqView(req_id)
  }
}