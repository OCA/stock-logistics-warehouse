/** @odoo-module **/

import {decrement, increment} from "@mail/model/model_field_command";
import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "MessagingNotificationHandler",
    recordMethods: {
        /**
         * @override
         */
        async _handleNotification(message) {
            if (message.type === "base.tier.validation/updated") {
                for (const reviewMenuView of this.messaging.models.ReviewerMenuView.all()) {
                    if (message.payload.review_created) {
                        reviewMenuView.update({extraCount: increment()});
                    }
                    if (message.payload.review_deleted) {
                        reviewMenuView.update({extraCount: decrement()});
                    }
                }
            }
            return this._super(message);
        },
    },
});
