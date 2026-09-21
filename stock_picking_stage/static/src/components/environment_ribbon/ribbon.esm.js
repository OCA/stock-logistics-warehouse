import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";

class PickingStageRibbon extends Component {
    static template = "picking.Ribbon";
    static props = {
        ...standardWidgetProps,
        field_name: {type: String},
        title: {type: String, optional: true},
        bgClass: {type: String, optional: true},
        bg_color_field: {type: String, optional: true},
    };
    static defaultProps = {
        title: "",
        bgClass: "text-bg-success",
        bg_color_field: "color",
    };

    get classes() {
        let classes = this.props.bgClass;
        const textDisplay = this.props.record.data[this.props.field_name];
        if (textDisplay.length > 15) {
            classes += " o_small";
        } else if (textDisplay.length > 10) {
            classes += " o_medium";
        }
        const colorFieldValue = this.props.record.data[this.props.bg_color_field];
        if (colorFieldValue) {
            classes += " o_colorlist_item_color_" + colorFieldValue;
        }
        return classes;
    }
}

export const pickingStageRibbon = {
    component: PickingStageRibbon,
    extractProps: ({attrs}) => {
        return {
            title: attrs.title,
            bgClass: attrs.bg_color,
            field_name: attrs.field_name,
            bg_color_field: attrs.bg_color_field,
        };
    },
    supportedAttributes: [
        {
            label: "Title",
            name: "title",
            type: "string",
        },
        {
            label: "Background color",
            name: "bg_color",
            type: "string",
        },
        {
            label: "Background color field name",
            name: "bg_color_field",
            type: "string",
        },
        {
            label: "Field name",
            name: "field_name",
            type: "string",
        },
    ],
};

registry.category("view_widgets").add("picking_stage_ribbon", pickingStageRibbon);
