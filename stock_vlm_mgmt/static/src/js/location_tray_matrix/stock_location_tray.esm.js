/** @odoo-module **/
/* Copyright 2024 Tecnativa - David Vidal
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).*/
import {Component, useEffect, useState} from "@odoo/owl";

import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

export class LocationTrayMatrixField extends Component {
    static template = "stock_vlm_mgmt.location_tray_matrix";
    static props = {
        ...standardFieldProps,
        click_action: {
            type: String,
            optional: true,
        },
    };

    setup() {
        super.setup();
        this.state = useState({matrix: this.props.record.data[this.props.name]});
        this.orm = useService("orm");
        this.action = useService("action");
        useEffect(
            () => {
                this.state.matrix = this.props.record.data[this.props.name];
            },
            () => [this.props.record.data[this.props.name]]
        );
    }
    /**
     *
     * @param {Event} event
     * @returns {Object} Odoo action
     */
    async onClickCell(event) {
        const coordinates = event.currentTarget.dataset.coordinates
            .split(",")
            .map((x) => {
                return parseInt(x, 10);
            });
        if (this.props.click_action) {
            const action = await this.orm.call(
                this.props.record.resModel,
                this.props.click_action,
                [this.props.record.resId],
                {
                    context: this.props.record.context || {},
                    pos_x: coordinates[0],
                    pos_y: coordinates[1],
                }
            );
            return this.action.doAction(action);
        }
        // This is for responsiveness
        this.state.matrix.selected = coordinates;
        // And here we propagate the changes to the field
        const currentValue = this.props.record.data[this.props.name] || {};
        const updatedValue = {...currentValue, selected: coordinates};
        this.props.record.update({[this.props.name]: updatedValue});
    }
}

registry.category("fields").add("stock_vlm_mgmt_location_tray_matrix", {
    component: LocationTrayMatrixField,
    supportedTypes: ["serialized"],
    extractProps: ({options}) => ({
        click_action: options.click_action,
    }),
});
