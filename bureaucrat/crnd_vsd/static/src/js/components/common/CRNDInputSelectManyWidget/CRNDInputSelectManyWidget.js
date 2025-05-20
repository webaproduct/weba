/** @odoo-module **/
import { Component, useState, onWillUpdateProps, onWillDestroy, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "../CRNDInputWidget";


export class CRNDInputSelectManyWidget extends CRNDInputWidget {
    static template = 'crnd_vsd.CRNDInputSelectManyWidget'

    static getPropsFromXml(fieldElement) {
        // <field name="select_any" widget="CRNDInputSelectWidget" required="true" default_value="3" title="Priority">
        //     <option value="1" name="First option"/>
        //     <option value="2" name="Second option"/>
        //     <option value="3" name="Third option"/>
        // </field>

        const data = {
            selectList: [],
        }

        const optionList = fieldElement.querySelectorAll('option')

        for (let i = 0; i < optionList.length; i++) {
            const option = optionList[i]
            let value = option.getAttribute('value')

            if (+value) {
                value = +value
            }

            data.selectList.push({
                value: value,
                name: option.getAttribute('name'),
            })
        }
        return data
    }

    setup() {
        this.state = useState({
            isOpen: false,
            items: [],
            activeItems: [],
            find_text: ''
        })

        this.updateItemsFromProps(this.props)

        onWillUpdateProps(nextProps => {
            this.updateItemsFromProps(nextProps)
        });

        useExternalListener(window, "click", this.closeMenu.bind(this), { capture: true });

        onWillDestroy(() => {
            window.removeEventListener("click", this.closeMenu.bind(this), { capture: true })
        })

        if (this.props.updateOnStart) {
            this.updateInputValue()
        }
    }

    updateInputValue() {
        const activeValues = []
        this.state.activeItems.forEach((activeObj) => {
            activeValues.push(activeObj.value)
        })
        const activeValuesWithName = [];
        this.state.activeItems.forEach((activeObj) => {
            activeValuesWithName.push({
                value: activeObj.value,
                name: activeObj.name,
            })
        })
        this.props._updateInputValue(this.props.name, activeValues, activeValuesWithName);
    }

    updateItemsFromProps(props) {
        if (props.selectList) {
            this.state.items = props.selectList
        }

        if ( !props.forceUpdateValue ) {
            if (!(props.default_value || props._form_value)) {
                return
            }
        }

        let valueList = []
        const props_default_value = eval(props.default_value)
        const propsValueSource = props_default_value ?? props._form_value

        if (propsValueSource) {
            for (let index in propsValueSource) {
                let value = propsValueSource[index]
                if (+value || value === "0") {
                    value = +value
                }
                valueList.push(value)
            }
        
        }

        const default_value = this.state.items.filter(x => valueList.includes(x.value))
        this.state.activeItems = default_value
    }



    isSorted(item) {
        if (this.state.find_text) {
            const regex = new RegExp(this.state.find_text, "i");
            return regex.test(item.name)
        }
        return true
    }

    isActive(item) {
        const active_item = this.state.activeItems.find(x => x.value == item.value)
        return Boolean(active_item)
    }

    onClickOption(itemObj) {
        this.state.isOpen = false;

        const activeItem = this.state.activeItems.find(x => x.value == itemObj.value)
        if (activeItem) {
            this.state.activeItems = this.state.activeItems.filter(x => x.value != activeItem.value)
        } else {
            this.state.activeItems.push(itemObj)
        }
        this.state.activeItems.item_obj
        this.updateInputValue();
    }

    onClickSelect() {
        if (this.state.items.length > 0) {
            this.state.isOpen = !this.state.isOpen;
        }
    }

    closeMenu(event) {
        const element = document.getElementById('crnd_widget_' + this.props.name)
        if (!element) {
            return;
        }

        const isClickInside = element.contains(event.target)
        if (!isClickInside) {
            this.state.isOpen = false;
        }
    }
}

CRNDInputSelectManyWidget.props = {
    ...CRNDInputSelectManyWidget,
    "is_find": {
        type: Boolean,
        optional: true,
    },
    "updateOnStart": {
        type: Boolean,
        optional: true,
        default: true,
    }
}