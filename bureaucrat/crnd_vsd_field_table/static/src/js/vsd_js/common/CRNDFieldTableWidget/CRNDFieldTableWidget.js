/** @odoo-module **/
import { Component, useState, onWillStart, onMounted, onPatched, onWillDestroy, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { CRNDInputWidget } from "@crnd_vsd/js/components/common/CRNDInputWidget";
import { CRNDInputBooleanWidget } from "@crnd_vsd/js/components/common/CRNDInputBooleanWidget/CRNDInputBooleanWidget";
import { CRNDInputIntegerWidget } from "@crnd_vsd/js/components/common/CRNDInputIntegerWidget/CRNDInputIntegerWidget";
import { CRNDInputTextWidget } from "@crnd_vsd/js/components/common/CRNDInputTextWidget/CRNDInputTextWidget";
import { CRNDInputTextareaWidget } from "@crnd_vsd/js/components/common/CRNDInputTextareaWidget/CRNDInputTextareaWidget";
import { CRNDInputDateWidget } from "@crnd_vsd/js/components/common/CRNDInputDateWidget/CRNDInputDateWidget";
import { CRNDInputDatetimeWidget } from "@crnd_vsd/js/components/common/CRNDInputDatetimeWidget/CRNDInputDatetimeWidget";
import { CRNDInputPriorityWidget } from "@crnd_vsd/js/components/common/CRNDInputPriorityWidget/CRNDInputPriorityWidget";
import { CRNDInputSelectWidget } from "@crnd_vsd/js/components/common/CRNDInputSelectWidget/CRNDInputSelectWidget";
import { CRNDInputSelectManyWidget } from "@crnd_vsd/js/components/common/CRNDInputSelectManyWidget/CRNDInputSelectManyWidget";
import { CRNDInputCheckboxListWidget } from "@crnd_vsd/js/components/common/CRNDInputCheckboxListWidget/CRNDInputCheckboxListWidget";
import { CRNDInputRadioListWidget } from "@crnd_vsd/js/components/common/CRNDInputRadioListWidget/CRNDInputRadioListWidget";


// ONLY FOR CREATE
export class CRNDFieldTableWidget extends CRNDInputWidget {
    static template = 'crnd_vsd_field_table.CRNDFieldTableWidget'
    static components = {
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

    static getPropsFromXml(fieldElement) {
        // <field name="select_any" widget="CRNDInputSelectWidget" required="true" default_value="3" title="Priority">
        //     <option value="1" name="First option"/>
        //     <option value="2" name="Second option"/>
        //     <option value="3" name="Third option"/>
        // </field>

        const fieldsList = []

        function fromAttributes(fieldElement) {
            const attrData = {}
            for (let i = 0; i < fieldElement.attributes.length; i++) {
                const attr = fieldElement.attributes[i]
                attrData[attr.name] = attr.value
            }
            return attrData
        }

        const fieldElements = fieldElement.querySelectorAll('fieldTable')

        for (let i = 0; i < fieldElements.length; i++) {
            const field = fieldElements[i]

            fieldsList.push({
                ...fromAttributes(field),
                ...CRNDFieldTableWidget.components[field.getAttribute('widget')].getPropsFromXml(field)
            })
        }
        return {
            fieldsList
        }
    }

    setup() {
        this.state = useState({
            rows: [
                {

                }
            ],
        })

        onMounted(() => {
            const fieldTableEl = document.querySelector(".field_table");
            this.inputsWithModals = fieldTableEl.querySelectorAll(".date_widget_input, .selection")

            let ticking = false;
            fieldTableEl.addEventListener("scroll", () => {
                if (!ticking) {
                    window.requestAnimationFrame(() => {
                        // reset the position on scroll
                        this.setModalsPositions();
                        ticking = false;
                    });
                    ticking = true;
                }
            });
            let ticking2 = false;
            window.addEventListener("scroll", () => {
                if (!ticking2) {
                    window.requestAnimationFrame(() => {
                        // reset the position on scroll
                        this.setModalsPositions();
                        ticking2 = false;
                    });
                    ticking2 = true;
                }
            }, true);
        })
        onPatched(() => {
            const fieldTableEl = document.querySelector(".field_table");
            this.inputsWithModals = fieldTableEl.querySelectorAll(".date_widget_input, .selection")
            this.setModalsPositions()
        })
    }

    setModalsPositions() {
        this.inputsWithModals.forEach((input) => {
            const rect = input.getBoundingClientRect();
            input.style.setProperty("--top", `${rect.top}px`);
            input.style.setProperty("--left", `${rect.left}px`);
        });
    }

    addRow() {
        this.state.rows.push({})
        
    }
    removeRow(index) {
        this.state.rows.splice(index, 1)
    }

    getProps(field, rowIndex) {
        const data = { ...field }
        data['_updateInputValue'] = (fieldName, value) => this.updateValue(rowIndex, fieldName, value)
        data['_form_value'] = this.state.rows[rowIndex][data.name]
        data['__all_form_values__'] = this.state.rows[rowIndex]
        delete data.title
        return data
    }
    
    updateValue(rowIndex, fieldName, value) {
        this.state.rows[rowIndex][fieldName] = value
        this.updateTableValue()
    }


    


    updateTableValue() {
        this.props._updateInputValue(
            'fieldtable', 
            this.state.rows, 
        );
    }

}

CRNDFieldTableWidget.props = {
    ...CRNDFieldTableWidget,
    "fieldsList": {
        type: Array,
        optional: false,
    },
}