/** @odoo-module **/
import { Component, useState, onWillStart, xml, markup, mount, onMounted, App } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { templates } from "@web/core/assets";
import { post } from "@web/core/network/http_service";
import { _t } from "@web/core/l10n/translation";

import { startParam } from "../../../features/startParam";

import { MainComponentsContainer } from "@web/core/main_components_container";

import { CRNDInputBooleanWidget } from "../../common/CRNDInputBooleanWidget/CRNDInputBooleanWidget";
import { CRNDInputIntegerWidget } from "../../common/CRNDInputIntegerWidget/CRNDInputIntegerWidget";
import { CRNDInputTextWidget } from "../../common/CRNDInputTextWidget/CRNDInputTextWidget";
import { CRNDInputTextareaWidget } from "../../common/CRNDInputTextareaWidget/CRNDInputTextareaWidget";
import { CRNDInputDateWidget } from "../../common/CRNDInputDateWidget/CRNDInputDateWidget";
import { CRNDInputDatetimeWidget } from "../../common/CRNDInputDatetimeWidget/CRNDInputDatetimeWidget";
import { CRNDInputPriorityWidget } from "../../common/CRNDInputPriorityWidget/CRNDInputPriorityWidget";
import { CRNDInputSelectWidget } from "../../common/CRNDInputSelectWidget/CRNDInputSelectWidget";
import { CRNDInputSelectManyWidget } from "../../common/CRNDInputSelectManyWidget/CRNDInputSelectManyWidget";
import { CRNDInputCheckboxListWidget } from "../../common/CRNDInputCheckboxListWidget/CRNDInputCheckboxListWidget";
import { CRNDInputRadioListWidget } from "../../common/CRNDInputRadioListWidget/CRNDInputRadioListWidget";

import { FileLoader } from "../../common/FileLoader/FileLoader";


export class RequestCreate extends Component {
    static template = "crnd_vsd.RequestCreate";
    static components = {
        FileLoader,
        MainComponentsContainer,
    }

    components = {
        CRNDInputBooleanWidget,
        CRNDInputIntegerWidget,
        CRNDInputTextWidget,
        CRNDInputTextareaWidget,
        CRNDInputDateWidget,
        CRNDInputDatetimeWidget,
        CRNDInputPriorityWidget,
        CRNDInputSelectWidget,
        CRNDInputSelectManyWidget,
        CRNDInputCheckboxListWidget,
        CRNDInputRadioListWidget,
    }

    setup() {
        this.created_app_list = {}
        this.rpc = useService("rpc");

        this.website_id = startParam.website_id;
        this.use_service_groups = startParam.use_service_groups;
        this.use_service = startParam.use_service;

        // enum
        this.tabNames = {
            service_group: 'service_group',
            service: 'service',
            category: 'category',
            type: 'type',
            request: 'request'
        }
        this.tabNamesList = Object.values(this.tabNames)


        this.state = useState({
            service_groups: [],
            services: [],
            categories: [],
            types: [],
            requestTemplate: null,

            files: [],

            activeTab: this.tabNames.service,

            formValues: {
                service: {
                    id: 0,
                    name: null,
                },
                category: {
                    id: 0,
                    name: null,
                },
                type: {
                    id: 0,
                    name: null,
                },
                requestData: {},
            },

            additionalDataForFields: {},

            canSave: true,
        })

        this.updateFilesList = this.updateFilesList.bind(this)
        this.removeFile = this.removeFile.bind(this)

        if (this.use_service_groups && this.use_service) {
            this.state.activeTab = this.tabNames.service_group
            this.state.formValues.service_group = {
                id: 0,
                name: null,
            }
        } else if (this.use_service) {
            this.state.activeTab = this.tabNames.service
        } else {
            this.state.activeTab = this.tabNames.category
        }

        onWillStart(async () => {
            await this.queryParamsHandler()

            if (this.use_service_groups && this.use_service) {
                await this.getGroups()
                if (!this.state.service_groups.length) {
                    this.changeActiveTab(this.tabNames.service)
                }
            } else if (this.use_service) {
                await this.getServices()
                if (!this.state.services.length) {
                    this.changeActiveTab(this.tabNames.category)
                }
            } else {
                await this.getCategories()
                if (!this.state.categories.length) {
                    this.changeActiveTab(this.tabNames.type)
                }
            }
        });

        this._updateInputValue = this._updateInputValue.bind(this)
    }

    isNumeric(value) {
        return /^-?\d+$/.test(value);
    }
    
    async queryParamsHandler() {
        // async for external modules

        const urlParams = new URLSearchParams(window.location.search);
        const parent_id = urlParams.get('parent_id');
        try {
            if (this.isNumeric(parent_id)) {
                this.state.formValues.parent_id = +parent_id
            }
        } catch (e) {

        }
    }

    updateFilesList(files) {
        this.state.files = files
    }
    removeFile(file) {
        this.state.files = this.state.files.filter(x => x.name != file.name && x.size != file.size)
    }

    async addAttachments(newReqID) {
        for (let i = 0; i < this.state.files.length; i++) {
            const file = this.state.files[i]
            const data = {
                csrf_token: startParam.csrf_token,
                ufile: file,
                thread_id: newReqID,
                thread_model: 'request.request',
                is_pending: false,
                temporary_id: -1,
            }

            const resp = await post('/mail/attachment/upload/', data)
        }
    }

    onClickHome() {
        window.location.href = "/requests"
    }

    getValueForSidePanel(field_name) {
        return this.state.formValues[field_name]?.name
    }

    changePage(indexDiff) {
        const tabIndex = this.tabNamesList.indexOf(this.state.activeTab) + indexDiff
        this.changeActiveTab(this.tabNamesList[tabIndex])
    }
    backBtnStatus() {
        if (this.use_service_groups) {
            return this.tabNamesList.indexOf(this.state.activeTab) > 0
        }
        return this.tabNamesList.indexOf(this.state.activeTab) > 1
    }
    nextBtnStatus() {
        return this.tabNamesList.indexOf(this.state.activeTab) < this.tabNamesList.length - 1
    }
    createBtnStatus() {
        return this.tabNamesList.indexOf(this.state.activeTab) == this.tabNamesList.length - 1
    }


    clearData(stage) {
        const defaultData = { id: 0, name: null }
        switch (stage) {
            case 'service_group':
                this.state.formValues.service = defaultData
            case 'service':
                this.state.formValues.category = defaultData
            case 'category':
                this.state.formValues.type = defaultData
            case 'type':
                this.state.formValues.requestData = {}

                this.cleanAppList()
        }
    }

    cleanAppList() {
        Object.values(this.created_app_list).forEach((app) => {
            app.destroy();
        })
        this.created_app_list = {}
    }

    changeData(key, data) {
        const nextActiveTab = this.tabNamesList.indexOf(key) + 1

        this.state.formValues[key] = {
            id: data.id,
            name: data.name,
        }
        this.changeActiveTab(this.tabNamesList[nextActiveTab])
        this.clearData(key)

    }

    async changeActiveTab(key) {
        if (key == this.tabNames.service_group && this.use_service_groups) {
            await this.getGroups()
        } else if (key == this.tabNames.service) {
            await this.getServices()
        } else if (key == this.tabNames.category) {
            await this.getCategories()
        } else if (key == this.tabNames.type) {
            await this.getTypes()
        } else if (key == this.tabNames.request) {
            await this.getRequestFormTemplate()
        }
        this.state.activeTab = key
    }

    async getGroups() {
        const groups = await this.rpc('/api/get_services_group', {
            website_id: this.website_id,
        })
        if (groups.length) {
            this.state.service_groups = groups
            if (
                groups.length == 1 
                && !this.state.formValues[this.tabNames.service_group]?.id
            ) {
                this.state.formValues[this.tabNames.service_group] = {
                    id: groups[0]?.id,
                    name: groups[0]?.name,
                }
                this.changeActiveTab(this.tabNames.service)
            }
        } else {
            this.changeActiveTab(this.tabNames.service)
        }
    }
    async getServices() {
        const payload = {
            website_id: this.website_id,
        }
        if (this.use_service_groups) {
            payload.service_group_id = this.state.formValues.service_group.id
        }
        const services = await this.rpc('/api/get_services', payload)
        if (services.length) {
            this.state.services = services
            if (
                services.length == 1
                && !this.state.formValues[this.tabNames.service]?.id
            ) {
                this.state.formValues[this.tabNames.service] = {
                    id: services[0]?.id,
                    name: services[0]?.name,
                }
                this.changeActiveTab(this.tabNames.category)
            }
        } else {
            this.changeActiveTab(this.tabNames.category)
        }
    }
    async getCategories() {
        const categories = await this.rpc('/api/get_categories', {
            website_id: this.website_id,
            service_id: this.state.formValues.service.id,
        })
        if (categories.length) {
            this.state.categories = categories
            if (
                categories.length == 1
                && !this.state.formValues[this.tabNames.category]?.id
            ) {
                this.state.formValues[this.tabNames.category] = {
                    id: categories[0]?.id,
                    name: categories[0]?.name,
                }
                this.changeActiveTab(this.tabNames.type)
            }
        }
    }
    async getTypes() {
        const types = await this.rpc('/api/get_types', {
            website_id: this.website_id,
            service_id: this.state.formValues.service.id,
            category_id: this.state.formValues.category.id
        })
        if (types.length) {
            this.state.types = types
            if (
                types.length == 1
                && !this.state.formValues[this.tabNames.type]?.id
            ) {
                this.state.formValues[this.tabNames.type] = {
                    id: types[0]?.id,
                    name: types[0]?.name,
                }
                this.changeActiveTab(this.tabNames.request)
            }
        }
    }

    async getCreateFieldsVisibility() {
        const visibleFields = await this.rpc('/api/get_create_fields_visibility', {
            website_id: this.website_id,
            service_id: this.state.formValues.service.id,
            type_id: this.state.formValues.type.id,
            category_id: this.state.formValues.category.id
        })
        this.state.visibleFields = visibleFields
    }

    getClassForTab(key) {
        const currentTabIndex = this.tabNamesList.indexOf(this.state.activeTab)
        const tabIndex = this.tabNamesList.indexOf(key)

        if (tabIndex < currentTabIndex) {
            return 'completed_step'
        } else if (tabIndex == currentTabIndex) {
            return 'active_step'
        } else {
            if (key == this.tabNames.request) {
                if (Object.keys(this.state.formValues.requestData).length > 0) {
                    return 'filled_step'
                }
            } else {
                if (this.state.formValues[key].id != 0) {
                    return 'filled_step'
                }
            }
        }

        return ''
    }

    getStatusForActiveItem(key, data) {
        if (this.state.formValues[key].id == data.id) {
            return 'active'
        }
        return ''
    }

    getItemStatusForMobile(key) {
        return this.state.activeTab == key
    }

    getNextBtnStatus() {
        return this.state.formValues[this.state.activeTab].id
    }






    _updateInputValue(fieldName, value) {
        this.state.formValues.requestData[fieldName] = value
        this.state.canSave = true
    }

    async createRequest() {
        this.state.canSave = false
        const createStatus = await this.rpc('/api/create_request', {
            website_id: this.website_id,
            ...this.state.formValues
        })
        if (createStatus.status_code == 422) {
            if ('required_fields' in createStatus) {
                this.state.errors_required = createStatus.required_fields.map(field_name => {
                    const field = this.fieldElements.find(x => x.getAttribute('name') === field_name);
                    return field ? (field.getAttribute('title') ?? field.getAttribute('placeholder')) : field_name;
                })
            }
        }
        if (createStatus.req_id) {
            await this.addAttachments(createStatus.req_id)
            window.location.href = `/requests/${createStatus.req_id}`
        }
    }




    // REQUEST
    getComponents() {
        return this.components;
    }

    timer(ms) { return new Promise(res => setTimeout(res, ms)); }

    async getRequestFormTemplate() {
        const template = await this.rpc('/api/get_requests_template', {
            website_id: this.website_id,
            service_id: this.state.formValues.service.id,
            type_id: this.state.formValues.type.id,
            category_id: this.state.formValues.category.id
        })
        console.log(template)
        await this.getCreateFieldsVisibility()

        const doc = this.createDoc(template.template)
        this.state.requestTemplate = this.getMarkupHTMLElement(doc)
        this.replaceWidgetOnTemplate(doc)
    }

    createDoc(template) {
        const parser = new DOMParser();
        return parser.parseFromString(markup(template), 'text/html');
    }

    async replaceWidgetOnTemplate() {
        this.cleanAppList()

        let fieldElements = []
        while (!fieldElements.length) {
            await this.timer(10)
            fieldElements = document.querySelectorAll('field')
        }
        this.fieldElements = Array.from(fieldElements)
        for (let i = 0; i < fieldElements.length; i++) {
            const field = fieldElements[i]
            const widgetName = field.getAttribute('widget');
            const ComponentClass = this.getComponents()[widgetName];

            if (ComponentClass) {
                const propsData = this.generatePropsDataForComponent(field, ComponentClass)

                const mountPoint = document.createElement('div');
                if (field.parentNode) {
                    field.parentNode.replaceChild(mountPoint, field);
                    if (document.body.contains(mountPoint)) {
                        const component = new App(ComponentClass, {
                            templates,
                            env: this.env,
                            props: propsData,
                            translateFn: _t,
                        })
                        component.mount(mountPoint);
                        this.created_app_list[field.getAttribute('name')] = component
                    } else {
                        console.error("Mount point is not in the DOM");
                    }
                } else {
                    console.error("The parent node is not available in the DOM");
                }
            }
        }
    }

    generatePropsDataForComponent(fieldElement, componentClass) {
        let data;

        function fromAttributes(fieldElement) {
            const attrData = {}
            for (let i = 0; i < fieldElement.attributes.length; i++) {
                const attr = fieldElement.attributes[i]
                attrData[attr.name] = attr.value
            }
            return attrData
        }

        data = fromAttributes(fieldElement)
        data['_updateInputValue'] = this._updateInputValue
        data['_form_value'] = this.state.formValues.requestData[data.name]
        data['__all_form_values__'] = this.state.formValues

        data = { ...data, ...componentClass.getPropsFromXml(fieldElement) }
        data['title'] = _t(data.title)
        return data
    }


    getMarkupHTMLElement(doc) {
        const bodyContent = doc.body.innerHTML;
        const div = document.createElement('div');
        div.innerHTML = bodyContent;
        const bodyHTML = div.innerHTML;

        return markup(bodyHTML)
    }
}