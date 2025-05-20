/** @odoo-module **/

// Importing required modules
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillRender } = owl;

// Creating a new component called StageButtons
export class StageButtons extends Component {
    setup() {
        super.setup(...arguments);

        // Setting up required services
        this.rpc = useService("rpc");
        this.actionService = useService("action");

        // Getting the current model
        this.model = this.env.model.root.resModel
        this.value_json = JSON.parse(this.props.record.data.stage_route_out_json);

        onWillRender(() => {
            this.value_json = JSON.parse(this.props.record.data.stage_route_out_json);
        });
    }
    //Method makes an Odoo RPC call to fetch updated properties
    _fetchUpdateProps() {
        this.rpc('/web/dataset/call_kw', {
            model: this.model,
            method: 'read',
            args: [[this.env.model.root.data['id']], ['stage_route_out_json']],
            kwargs: {},
        }).then((result) => {
            // Trigger change state to update component
            this.value_json = JSON.parse(result[0]['stage_route_out_json']);

            // it is important to pass resId of model to load!
            this.env.model.load({ resId: this.env.model.root.data.id });
        });
    };

    // Method called when a button is clicked
    async _onButtonClick(routeId) {
        // Save the record before moving request to assure we can do it
        await this.env.model.root.save({
                noReload: true,
                stayInEdition: true,
                useSaveErrorDialog: true,
            });

        // Calling an Odoo RPC to execute an API request to provide button route
        if (this.env.model.root.data['id']) {
            return this.rpc('/web/dataset/call_kw', {
                model: this.model,
                method: 'api_move_request',
                args: [this.env.model.root.data['id'], routeId],
                kwargs: {},
            }).then((action_data) => {
                // If the RPC call returns an action, execute it
                if (action_data) {
                    this.actionService.doAction(
                        action_data, {
                        // after wizard closing, update props to render new stage buttons
                            onClose: () => {
                                this._fetchUpdateProps();
                            },
                        }
                    )
                // If the RPC call returns nothing, update props to render new stage buttons
                } else {
                    this._fetchUpdateProps();
                }
            })
    };
}}
// Setting the component template
StageButtons.template = 'generic_request.stage_buttons'

//// Registering the component in the "fields" category of the Odoo registry
registry.category('fields').add('stage_route_out_widget', {component: StageButtons});
