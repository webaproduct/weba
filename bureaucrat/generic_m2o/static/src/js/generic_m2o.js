/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {
    m2oTupleFromData,
    many2OneField,
    Many2OneField
} from '@web/views/fields/many2one/many2one_field';
import {useOwnedDialogs} from "@web/core/utils/hooks";
import {sprintf} from "@web/core/utils/strings";
import {
    Many2XAutocomplete,
    useOpenMany2XRecord
} from "@web/views/fields/relational_utils";
import {
    SelectCreateDialog
} from "@web/views/view_dialogs/select_create_dialog";

const {onPatched} = owl;

function useGenericSelectCreate({
                                    resModel,
                                    activeActions,
                                    onSelected,
                                    onCreateEdit
                                }) {
    const addDialog = useOwnedDialogs();

    function selectCreate({domain, context, filters, title, forceModel}) {
        addDialog(SelectCreateDialog, {
            title: title || _t("Select records"),
            noCreate: !activeActions.create,
            multiSelect: "link" in activeActions ? activeActions.link : false, // LPE Fixme
            resModel: forceModel || resModel,
            context,
            domain,
            onSelected,
            onCreateEdit: () => onCreateEdit({context}),
            dynamicFilters: filters,
        });
    }
    return selectCreate;
}

class GenericMany2XAutocomplete extends Many2XAutocomplete {
    setup() {
        super.setup(...arguments);
        const {activeActions, resModel, update} = this.props;
        this.selectCreate = useGenericSelectCreate({
            resModel,
            activeActions,
            onSelected: (resId) => {
                const resIds = Array.isArray(resId) ? resId : [resId];
                const values = resIds.map((id) => ({id}));
                return update(values);
            },
            onCreateEdit: ({context}) => this.openMany2X({context}),
        });
    }

    async loadOptionsSource(request) {
        if (!this.props.resModel) {
            return [];
        }
        return await super.loadOptionsSource(...arguments);
    }

    async onSearchMore(request) {
        const {resModel, getDomain, context, fieldString} = this.props;

        const domain = getDomain();
        let dynamicFilters = [];
        if (request.length) {
            const nameGets = await this.orm.call(resModel, "name_search", [], {
                name: request,
                args: domain,
                operator: "ilike",
                limit: this.props.searchMoreLimit,
                context,
            });

            dynamicFilters = [
                {
                    description: sprintf(_t("Quick search: %s"), request),
                    domain: [["id", "in", nameGets.map((nameGet) => nameGet[0])]],
                },
            ];
        }

        const title = sprintf(_t("Search: %s"), fieldString);
        this.selectCreate({
            domain,
            context,
            filters: dynamicFilters,
            title,
            forceModel: resModel,
        });
    }
}

GenericMany2XAutocomplete.template = 'generic_m2o.GenericMany2XAutocomplete';

export class GenericMany2OneField extends Many2OneField {
    static template = "generic_m2o.GenericMany2OneField";
    static supportedTypes = ['integer', 'many2one_reference']
    static components = {
        ...Many2OneField.components,
        GenericMany2XAutocomplete,
    };
    static props = {
        ...Many2OneField.props,
        value: true,
        modelField: {
            type: String,
            optional: true,
        },
    };

    setup() {
        super.setup(...arguments);
        this.modelField = this.props.modelField;
        if (!this.modelField) {
            const fieldName = this.props.name;
            const modelFieldFromFieldAttrs = this.props.record.fields[fieldName].model_field;
            if (modelFieldFromFieldAttrs) {
                this.modelField = modelFieldFromFieldAttrs;
            } else {
                throw new Error(`Field "${fieldName}" must have the "model_field" parameter`);
            }
        }
        if (!(this.modelField in this.props.record.data)) {
            throw new Error(`The field specified in parameter "model_field" was not found in the form view`);
        }
        if (Object.keys(this.props.record.data).includes(this.props.name)) {
            this.props.value = this.props.record.data[this.props.name];
        }
        onPatched(this.onPatched)
        this.currentRelationModel = this.relationModel;
        this.currentRecordId = this.props.record.id;
        this.state.proxyDisplayName = false;
        this.state.relationModel = this.relationModel;
        this.state.modelField = this.modelField;

        this.updateProxyDisplayName();

        // Quick Create is disabled because it is not possible to correctly extend the 'web.BasicModel'
        this.quickCreate = null;

        this.openMany2X = useOpenMany2XRecord({
            resModel: this.relation,
            activeActions: this.state.activeActions,
            isToMany: false,
            onRecordSaved: async (record) => {
                await this.props.record.load();
                await this.proxyUpdate(m2oTupleFromData(record.data));
                if (this.props.record.model.root.id !== this.props.record.id) {
                    this.props.record.switchMode("readonly");
                }
            },
            onClose: () => this.focusInput(),
            fieldString: this.props.string,
        });

        this.update = (value, params = {}) => {
            if (value) {
                value = m2oTupleFromData(value[0]);
            }
            this.state.isFloating = false;
            return this.proxyUpdate(value);
        };
    }

    onPatched() {
        let changedRelationModel = false;
        let changedRecord = false;
        if (this.currentRelationModel !== this.relationModel) {
            this.currentRelationModel = this.relationModel;
            changedRelationModel = true;
        }
        if (this.currentRecordId !== this.props.record.id) {
            this.currentRecordId = this.props.record.id;
            changedRecord = true;
        }
        if (changedRelationModel || changedRecord) {
            this.state.relationModel = this.relationModel;
            if (!changedRecord) {
                this.props.record.update(false);
            } else {
                this.updateProxyDisplayName();
            }
        }
    }

    updateProxyDisplayName(resId) {
        if (!resId) {
            resId = this.props.value;
        }
        if (!this.relationModel || !resId || typeof(resId) !== 'number'){
            return;
        }
        this.orm.call(this.relationModel, 'name_get', [[resId]])
            .then((data) => {
                this.state.proxyDisplayName = data[0][1];
            }).catch(() => {
                this.state.proxyDisplayName = false;
            });
    }

    get relationModel() {
        return this.props.record.data[this.modelField];
    }

    get relation() {
        return this.state.relationModel || this.props.record.data.res_model;
    }

    get displayName() {
        return (this.proxyValue && this.proxyValue[1]) ? this.proxyValue[1].split("\n")[0] : '';
    }

    get extraLines() {
        return this.displayName ? this.displayName.split("\n").map((line) => line.trim()).slice(1) : [];
    }

    get resId() {
        let val = this.proxyValue;
        return val && val[0];
    }

    async openDialog(resId) {
        return this.openMany2X({
            resId,
            forceModel: this.relationModel,
            context: this.context,
        });
    }

    get proxyValue() {
        return this.props.value
            ? [this.props.value, this.state.proxyDisplayName]
            : false;
    }

    proxyUpdate(value) {
        let resId = false;
        let displayName = false;
        this.props.value = value ? value[0] : value;
        if (value) {
            displayName = value[1] || false;
            resId = value[0];
        }
        this.state.proxyDisplayName = displayName;
        if (!displayName) {
            this.updateProxyDisplayName(resId);
        }
        let vals = {};
        vals[this.props.name] = resId
        this.props.record.update(vals);
    }
}

export const genericMany2OneField = {
    ...many2OneField,
    component: GenericMany2OneField,
    extractProps(fieldInfo, dynamicInfo) {
        const props = {
            ...many2OneField.extractProps(...arguments),
            modelField: fieldInfo.attrs.model_field,
            value: fieldInfo.attrs.value || true,
        }
        return props;
    },
};

registry.category('fields').add('generic_m2o', genericMany2OneField);
