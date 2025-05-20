/** @odoo-module **/
import { Component } from "@odoo/owl";
import { redirectToReqView } from "../../../../../features/utils";

export class RequestsListKanbanItem extends Component {
  static template = "crnd_vsd.RequestsListKanbanItem";

  clickOnReqName(req_id) {
    redirectToReqView(req_id)
  }
}