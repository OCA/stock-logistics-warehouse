/** @odoo-module **/

import {attr, many, one} from "@mail/model/model_field";
import {registerModel} from "@mail/model/model_core";

registerModel({
    name: "ReviewGroup",
    modelMethods: {
        convertData(data) {
            return {
                domain: data.domain,
                irModel: {
                    iconUrl: data.icon,
                    id: data.id,
                    model: data.model,
                    name: data.name,
                },
                pending_count: data.pending_count,
            };
        },
    },
    recordMethods: {
        /**
         * @private
         */
        _onChangePendingCount() {
            if (this.type === "tier_review" && this.pending_count === 0) {
                this.delete();
            }
        },
    },
    fields: {
        reviewGroupViews: many("ReviewGroupView", {
            inverse: "reviewGroup",
        }),
        domain: attr(),
        irModel: one("ir.model.review", {
            identifying: true,
            inverse: "reviewGroup",
        }),
        pending_count: attr({
            default: 0,
        }),
        type: attr(),
    },
    onChanges: [
        {
            dependencies: ["pending_count", "type"],
            methodName: "_onChangePendingCount",
        },
    ],
});
