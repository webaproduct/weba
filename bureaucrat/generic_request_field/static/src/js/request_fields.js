/** @odoo-module **/

// Importing required modules
import { registry } from "@web/core/registry";
const { Component, useState, onWillUpdateProps } = owl;

// Creating a new component called RequestFields
class RequestFields extends Component {
    setup() {
        super.setup(...arguments);

        // Setting up component state
        this.state = useState({
            value_json: JSON.parse(this.props.value),
        });
        // Updating the component state when the props change
        onWillUpdateProps(nextProps => {
            if (nextProps.value !== this.props.value) {
                this.state.value_json = JSON.parse(nextProps.value);
            }
        });
    }
    _updateInputValue(event) {
        var field_id = event.target.dataset.field_id;
        var input_value = event.target.value;
        this.state.value_json.fields_info[field_id].value = input_value;
        this.props.update(JSON.stringify(this.state.value_json));
  }
}
// Setting the component template
RequestFields.template = 'generic_request_field.request_fields'

// Registering the component in the "fields" category of the Odoo registry
registry.category('fields').add('request_fields', RequestFields);
