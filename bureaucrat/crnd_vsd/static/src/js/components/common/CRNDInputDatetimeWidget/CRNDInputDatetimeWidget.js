/** @odoo-module **/
import { CRNDInputDateWidget } from "../CRNDInputDateWidget/CRNDInputDateWidget";
import { startParam } from "../../../features/startParam";


export class CRNDInputDatetimeWidget extends CRNDInputDateWidget {
    setup() {
        super.setup()

        this.state.pickerProps.type = "datetime"

        let { time_format } = startParam;
        this.state.timeFormat = time_format.replace("%H", "HH").replace("%M", "mm").replace("%S", "ss") || 'HH:mm'
    }

    getRegexForValidate() {
        return /^[0-9 .:/]+$/;
    }

    getDateTimeText(datetime) {
        let { date_format, time_format } = startParam;
        date_format = date_format.replace("%d", "dd").replace("%m", "MM").replace("%Y", "yyyy")
        time_format = time_format.replace("%H", "HH").replace("%M", "mm").replace("%S", "ss")
        
        return datetime ? datetime.toFormat(`${date_format} ${time_format}`) : (this.props.placeholder || '-');
    }

    getFormat() {
        return `${this.state.dateFormat} ${this.state.timeFormat}`;
    }
}