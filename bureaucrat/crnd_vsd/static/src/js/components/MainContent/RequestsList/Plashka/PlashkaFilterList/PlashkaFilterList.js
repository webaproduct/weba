/** @odoo-module **/
import { Component, onWillUpdateProps, useState } from "@odoo/owl";


export class PlashkaFilterList extends Component {
    static template = "crnd_vsd.PlashkaFilterList";


    setup() {
        this.state = useState({
            active_filters: Object.keys(this.props.filterData).map((key) => [key, this.props.filterData[key]]) || [],
        })

        onWillUpdateProps(nextProps => {
            this.state.active_filters = Object.keys(nextProps.filterData).map((key) => [key, nextProps.filterData[key]]) || []
        });
    }

    isActiveFilters() {
        let activeFilterCount = 0
        Object.values(this.props.filterData)?.forEach(filter => {
            if (this.isValidFilter(filter)) activeFilterCount++
        });
        return activeFilterCount
    }

    isValidFilter(filter) {
        if (filter?.value) {
            if (Array.isArray(filter.value) && filter.value.length) return true
        }
        return false
    }
}