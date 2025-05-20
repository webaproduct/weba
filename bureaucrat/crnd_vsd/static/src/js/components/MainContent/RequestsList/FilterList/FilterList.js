/** @odoo-module **/
import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

import { startParam } from "../../../../features/startParam";

import { CRNDInputTextWidget } from "../../../common/CRNDInputTextWidget/CRNDInputTextWidget";
import { CRNDInputSelectWidget } from "../../../common/CRNDInputSelectWidget/CRNDInputSelectWidget";
import { CRNDInputDateWidget } from "../../../common/CRNDInputDateWidget/CRNDInputDateWidget";
import { CRNDInputSelectManyWidget } from "../../../common/CRNDInputSelectManyWidget/CRNDInputSelectManyWidget";


export class FilterList extends Component {
    static template = "crnd_vsd.FilterList";
    static components = {
        CRNDInputTextWidget,
        CRNDInputSelectWidget,
        CRNDInputDateWidget,
        CRNDInputSelectManyWidget
    }

    fields = {
        'global_search': {
            title: _t('Request search'),
            icon_url: false,
        },
        'service_id': {
            title: _t('Request service'),
            icon_url: '/crnd_vsd/static/img/service.svg',
        },
        'category_id': {
            title: _t('Request category'),
            icon_url: '/crnd_vsd/static/img/category.svg',
        },
        'type_id': {
            title: _t('Request type'),
            icon_url: '/crnd_vsd/static/img/type.svg',
        },
        'create_date_from': {
            title: _t('Request create date from'),
            icon_url: false,
        },
        'create_date_to': {
            title: _t('Request create date to'),
            icon_url: false,
        },
    }

    setup() {
        this.rpc = useService("rpc");

        this.website_id = startParam.website_id;
        this.use_service = startParam.use_service;
    

        this.state = useState({
            filterData: {},
            services: [],
            categories: [],
            types: [],
            reqStatus: this.props.reqStatus,
            
            updateMarker: 0,
        })
    
        this.setValue = this.setValue.bind(this)

        onWillUpdateProps(nextProps => {
            this.state.reqStatus = nextProps.reqStatus

            if (nextProps.filterData) {
                this.state.filterData = JSON.parse(JSON.stringify(nextProps.filterData));
            }
            this.state.updateMarker++
        });

        onWillStart(async () => {
            if (this.props.filterData) {
                this.state.filterData = JSON.parse(JSON.stringify(this.props.filterData));
            }

            await this.getAdditionalData();
        })
    }

    getPropsForInput(key, many=false) {
        let data = {};
        data['_updateInputValue'] = this.setValue
        let value = this.state.filterData[key]?.value
        if (Array.isArray(value) && value.length) {
            if (many) {
                value = value?.map(x => x.value)
            } else {
                value = value[0]?.value
            }
        } else if (typeof value === 'object' && value !== null) {
            value = value?.value
        }
        data['_form_value'] = value
        data['forceUpdateValue'] = true
        data['name'] = key
        data['required'] = false
        data['placeholder'] = this.fields[key]?.title
        data['icon_url'] = this.fields[key]?.icon_url
        data['reloadComponent'] = this.state.updateMarker
        return data
    }

    setValue(key, value, valueWithName) {
        // if (Array.isArray(value) && !value?.length) return
        if (this.state.filterData[key]?.value == value) return
        if (this.state.filterData[key]?.value?.value == value) return

        this.state.filterData[key] = {
            name: this.fields[key]?.title,
            icon_url: this.getIconByKey(key),
            value: valueWithName
        };
    }

    getIconByKey(key) {
        return this.fields[key]?.icon_url
    }

    reset() {
        // this.state.filterData = JSON.parse(JSON.stringify(this.props.filterData)) || {};
        this.state.filterData = {};
        this.props.deleteAllFilters();
        this.props.toggleFilterList(false);
    }

    save() {
        const filterResult = {}
        for (const [key, filter] of Object.entries(this.state.filterData)) {
            const data = {
                name: filter?.name,
                icon_url: filter?.icon_url,
            }
            const value = filter?.value
            if (!value) {
                continue
            } else if (key == 'global_search'){
                data.value = value?.value
            } else if (Array.isArray(value)) {
                data.value = value
            } else {
                data.value = [value]
            }
            filterResult[key] = data
        }
        
        this.props.saveFilterList(filterResult);
        this.props.changeRequestStatus(this.state.reqStatus);
        this.props.toggleFilterList(false);
    }
    
    
    close(e) {
        this.props.toggleFilterList(false);
    }

    async getAdditionalData() {
        if (this.use_service) {
            await this.getFilterServices();
        }
        await this.getFilterCategories();
        await this.getFilterTypes();
    }

    async getFilterServices() {
        const payload = {
            website_id: this.website_id,
        }
        const services = await this.rpc('/api/get_services', payload)
        if (services.length) {
            this.state.services = services.map(item => ({
                value: item.id,
                name: item.name
              }))
        }
    }
    async getFilterCategories() {
        const categories = await this.rpc('/api/get_categories', {
            website_id: this.website_id,
            filter_by_service: false,
        })
        if (categories.length) {
            this.state.categories = categories.map(item => ({
                value: item.id,
                name: item.name
              }))
        }
    }
    async getFilterTypes() {
        const types = await this.rpc('/api/get_types', {
            website_id: this.website_id,
            filter_by_service: false,
            filter_by_category: false,
        })
        if (types.length) {
            this.state.types = types.map(item => ({
                value: item.id,
                name: item.name
              }))
        }
    }
}