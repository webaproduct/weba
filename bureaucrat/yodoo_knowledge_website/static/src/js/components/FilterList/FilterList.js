/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

import { startParam } from "../../features/startParam";

import { YodooInputSelectWidget } from "../common/YodooInputSelectWidget/YodooInputSelectWidget";
// import { CRNDInputTextWidget } from "../../../common/CRNDInputTextWidget/CRNDInputTextWidget";
// import { CRNDInputSelectWidget } from "../../../common/CRNDInputSelectWidget/CRNDInputSelectWidget";
// import { CRNDInputDateWidget } from "../../../common/CRNDInputDateWidget/CRNDInputDateWidget";
// import { CRNDInputSelectManyWidget } from "../../../common/CRNDInputSelectManyWidget/CRNDInputSelectManyWidget";


export class FilterList extends Component {
    static template = "yodoo_knowledge_website.FilterList";
    static components = {
        YodooInputSelectWidget,
        // CRNDInputTextWidget,
        // CRNDInputSelectWidget,
        // CRNDInputDateWidget,
        // CRNDInputSelectManyWidget
    }

    titleByKeyMapping = {
        'item_format': _t('Item format'),
        'item_type_id': _t('Item type'),
        'tag': _t('Tag'),
    }


    setup() {
        
        this.rpc = useService("rpc");

        this.website_id = startParam.website_id;
    

        this.state = useState({
            filterData: {},
            tags: [],
            item_types: [],
            item_formats: [
                {
                    value: 'pdf',
                    name: 'PDF',
                },
                {
                    value: 'html',
                    name: 'HTML',
                },
            ]
        })
    
        this.setValue = this.setValue.bind(this)

        onWillStart(async () => {
            if (this.props.filterData) {
                this.state.filterData = JSON.parse(JSON.stringify(this.props.filterData));
            }

            await this.getFilterTags();
            await this.getFilterItemTypes();
        })
    }

    getPropsForInput(key) {
        let data = [];
        data['_updateInputValue'] = (value) => this.setValue(key, value)
        data['_form_value'] = this.state.filterData[key]
        data['name'] = key
        data['placeholder'] = this.titleByKeyMapping[key]
        return data
    }

    setValue(key, value) {
        if (value) {
            if (Array.isArray(value)) {
                if (value?.length) {
                    this.state.filterData[key] = value
                } else {
                    delete this.state.filterData[key]

                }
            } else {
                this.state.filterData[key] = [value]
            }
        } else {
            delete this.state.filterData[key]
        }
    }

    reset() {
        // this.state.filterData = JSON.parse(JSON.stringify(this.props.filterData)) || {};
        this.state.filterData = {};
        this.save();
    }

    save() {
        const filterResult = {}
        for (const [key, value] of Object.entries(this.state.filterData)) {
            if (!value) {
                continue
            } else if (key == 'global_search'){
                filterResult[key] = value
            } else if (Array.isArray(value)) {
                filterResult[key] = value
            } else {
                filterResult[key] = [value]
            }
        }
        
        this.props.saveFilterList(filterResult);
        this.props.toggleFilterList(false);
    }
    
    
    close(e) {
        this.props.toggleFilterList(false);
    }

    async getFilterItemTypes() {
        const item_types = await this.rpc('/yodoo_knowledge_website/api/get_item_types', {
            website_id: this.website_id,
        })
        if (item_types.length) {
            this.state.item_types = item_types.map(item_type => ({
                value: item_type.id,
                name: item_type.name
              }))
        }
    }
    async getFilterTags() {
        const tags = await this.rpc('/yodoo_knowledge_website/api/get_tags', {
            website_id: this.website_id,
        })
        if (tags.length) {
            this.state.tags = tags.map(tag => ({
                value: tag.id,
                name: tag.name
              }))
        }
    }
}