/** @odoo-module **/
import { Component, useState, onWillUpdateProps, useExternalListener, onWillDestroy, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { DateTimePickerPopover } from "@web/core/datetime/datetime_picker_popover";
import { CRNDInputWidget } from "../CRNDInputWidget";
import { startParam } from "../../../features/startParam";
import { parseDateTime } from "@web/core/l10n/dates";


export class CRNDInputDateWidget extends CRNDInputWidget {
    static template = 'crnd_vsd.CRNDInputDateWidget'
    static components = {
        DateTimePickerPopover,
    }

    setup() {
        this.crnd_date_el = useRef('crnd_date_widget')
        this.state = useState({
            datetime: null,
            rawDatetime: null,

            isDatetimePickerOpen: false,
            pickerProps: {
                daysOfWeekFormat: "short",
                focusedDateIndex: 0,
                maxPrecision: "decades",
                minPrecision: "days",
                onSelect: (value) => {this.updateInputValue(value)},
                range: false,
                rounding: 5,
                type: "date",
            },

            dateFormat: 'dd/mm/YYYY',
        })
        this.updateInputValue(this.props.default_value || this.props._form_value || null)

        let { date_format, time_format } = startParam;
        if (date_format) {
            this.state.dateFormat = date_format.replace("%d", "dd").replace("%m", "MM").replace("%Y", "yyyy")
        }

        onWillUpdateProps(nextProps => {
            this.updateInputValue(nextProps.default_value || nextProps._form_value || null)
        });

        this.closeDatetimePicker = this.closeDatetimePicker.bind(this)
        this.openDatetimePicker = this.openDatetimePicker.bind(this)


        useExternalListener(window, "click", this.closeDatetimePicker.bind(this), { capture: true });
        useExternalListener(window, "keydown", this.resetDatetime.bind(this));

        onWillDestroy(() => {
            window.removeEventListener("click", this.closeDatetimePicker.bind(this), { capture: true })
        })

    }

    
    openDatetimePicker() {
        this.state.isDatetimePickerOpen = true
    }
    resetDatetime(event) {
        if (this.state.isDatetimePickerOpen == true) {
            const keyID = event.keyCode;
    
            // 8 - backspace, 46 - delete
            if (keyID == 46) {
                this.updateInputValue(null)
            }
        }
    }
    enterOnDatetime(event) {
        // 13 - Enter
        if (event.keyCode === 13) {
            this.onChangeContentEditable()
        }
    }
    validate(event) {
        var theEvent = event;

        // Handle paste
        if (theEvent.type === 'paste') {
            key = event.clipboardData.getData('text/plain');
        } else {
        // Handle key press
            var key = theEvent.keyCode || theEvent.which;
            key = String.fromCharCode(key);
        }
        var regex = this.getRegexForValidate()
        if( !regex.test(key) ) {
            theEvent.returnValue = false;
            if(theEvent.preventDefault) theEvent.preventDefault();
        }
    }

    getRegexForValidate() {
        return /^[0-9 ./]$/;
    }

    closeDatetimePicker(event, hard=false) {
        if (hard) {
            this.state.isDatetimePickerOpen = false
            return
        }
        const element = document.getElementById('crnd_widget_' + this.props.name)
        if (!element) {
            return;
        }

        const isClickInside = element.contains(event.target)
        if (!isClickInside) {
            this.state.isDatetimePickerOpen = false
        }
    }

    updateInputValue(value) {
        // Luxon datetype
        if (typeof value == 'string') value = luxon.DateTime.fromISO(value)
        if (value?.ts == this.state.datetime?.ts) {
            this.state.isDatetimePickerOpen = false
            return
        }
        this.state.datetime = value;
        this.state.rawDatetime = this.state.datetime ? this.state.datetime.toFormat(this.getFormat()) : null
        this.state.pickerProps.value = this.state.datetime
        this.props._updateInputValue(this.props.name, value ? value.toISO() : null)
    }

    getPlaceholder() {
        if (!this.state.isDatetimePickerOpen) {
            return (this.props.placeholder || '-');
        } else {
            return `Type in format - ${this.getFormat()}` 
        }
    }

    getFormat() {
        return this.state.dateFormat
    }

    onChangeContentEditable() {
        const value = this.crnd_date_el.el.value
        if (value) {
            const date = this.safeConvert(value);
            if (date) {
                this.updateInputValue(date);
            } else {
                this.crnd_date_el.el.value = this.state.rawDatetime
            }
        } else {
            this.updateInputValue(null);
        }
    }



    safeConvert(value) {
        try {
            return parseDateTime(value, { format: this.getFormat() });
        } catch (error) {
            return null
        }
    };
}