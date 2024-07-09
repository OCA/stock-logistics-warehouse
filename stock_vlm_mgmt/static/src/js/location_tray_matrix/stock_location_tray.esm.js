/** @odoo-module **/
/* Copyright 2024 Tecnativa - David Vidal
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).*/
import {Component, useState} from "@odoo/owl";

import {_lt} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

export class LocationTrayMatrixField extends Component {
    setup() {
        this.state = useState(this.props.value);
        this.orm = useService("orm");
        this.action = useService("action");
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
            const action = this.orm.call(
                this.props.record.resModel,
                this.props.click_action,
                [[this.props.record.data.id]],
                {pos_x: coordinates[0], pos_y: coordinates[1]}
            );
            return this.action.doAction(action);
        }
        // This is for responsiveness
        this.state.selected = coordinates;
        // And here we propagate the changes to the field
        this.props.value.selected = coordinates;
        this.props.update(this.props.value);
    }
}

LocationTrayMatrixField.template = "stock_vlm_mgmt.location_tray_matrix";
LocationTrayMatrixField.props = {
    ...standardFieldProps,
    click_action: {
        type: String,
        optional: true,
    },
};
LocationTrayMatrixField.extractProps = ({attrs}) => {
    if ("click_action" in attrs.options) {
        return {click_action: attrs.options.click_action};
    }
};

LocationTrayMatrixField.displayName = _lt("Tray storage layout");
LocationTrayMatrixField.supportedTypes = ["serialized"];

registry.category("fields").add("location_tray_matrix", LocationTrayMatrixField);
