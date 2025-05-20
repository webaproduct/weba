/** @odoo-module **/
import { Component } from "@odoo/owl";
import { RequestsListKanbanItem } from "./RequestsListKanbanItem/RequestsListKanbanItem";

export class RequestsListKanban extends Component {
  static template = "crnd_vsd.RequestsListKanban";
  static components = {
    RequestsListKanbanItem
  }

}