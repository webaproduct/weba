/** @odoo-module **/
import { Component, useState, onWillStart, onWillUpdateProps, onWillDestroy, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";



export class YodooInputSelectWidget extends Component {
    static template = 'yodoo_knowledge_multilanguage_website.YodooInputSelectWidget'

    setup() {
        this.state = useState({
            isOpen: false,
            items: [],
            active: false,
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
    }

    updateItemsFromProps(props) {
        if (props.selectList) {
            this.state.items = props.selectList
        }
        if (props.default_value || props._form_value) {
            let value = props.default_value || props._form_value
            if (+value) {
                value = +value
            }

            const default_value = this.state.items.find(x => x.value == value)
            if (default_value) {
                this.state.active = default_value
            } else {
                this.state.active = false
            }
        }
        if (props._form_value == null) {
            this.state.active = false
        }
    }

    updateInputValue() {
        this.props._updateInputValue(this.state.active.value);
    }


    isActive(item) {
        return this.state.active?.value == item.value
    }

    isSorted(item) {
        if (this.state.find_text) {
            const regex = new RegExp(this.state.find_text, "i");
            return regex.test(item.name)
        }
        return true
    }

    onClickOption(item_obj) {
        this.state.isOpen = false;
        this.state.active = item_obj
        this.updateInputValue();
    }

    onClickSelect() {
        if (this.state.items.length > 0) {
            this.state.isOpen = !this.state.isOpen;
        }
    }

    closeMenu(event) {
        const element = document.getElementById('yodoo_widget_' + this.props.name)
        if (!element) {
            return;
        }

        const isClickInside = element.contains(event.target)
        if (!isClickInside) {
            this.state.isOpen = false;
        }
    }
}

YodooInputSelectWidget.props = {
    options: {
        type: Array[Object],
        required: true,
    },
    modelValue: {},
    "selectList": {
        type: Array,
        optional: false,
    },
    "is_find": {
        type: Boolean,
        optional: true,
    },

}