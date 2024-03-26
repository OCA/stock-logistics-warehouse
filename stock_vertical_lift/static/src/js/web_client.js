odoo.define("stock_vertical_lift.WebClient", function (require) {
    "use strict";

    const WebClient = require("web.WebClient");
    // Web_notify.WebClient is needed to be loaded beforehand: we can't extend it
    // directly, but we'll override its method ``bus_notification``
    require("web_notify.WebClient");

    WebClient.include({
        /**
         * Override method to filter out shuttle notifications that are not for the current device
         *
         * @override
         **/
        bus_notification: function (notifications) {
            const shuttle_notifications = notifications.filter((n) =>
                this.is_shuttle_notification(n)
            );
            if (shuttle_notifications.length > 0) {
                const filtered_shuttle_notifications = this.filter_shuttle_notifications(
                    shuttle_notifications
                );
                // Notifications will be displayed if:
                // 1) they're not shuttle-related
                // 2) they're included in the filtered shuttle notifications
                // NB: using ``filter`` allows keeping notifications' order
                notifications = notifications.filter(
                    (n) =>
                        !this.is_shuttle_notification(n) ||
                        filtered_shuttle_notifications.indexOf(n) !== -1
                );
            }
            this._super(notifications);
        },

        is_shuttle_notification: function (notification) {
            const values = notification[1];
            return (
                !_.isUndefined(values.params) &&
                !_.isUndefined(values.params.shuttle_info)
            );
        },

        filter_shuttle_notifications: function (notifications) {
            const filtered_notifications = [];
            const url_hash = new URLSearchParams(window.location.hash.replace("#", ""));
            const rec_model = url_hash.get("model");
            const rec_id = parseInt(url_hash.get("id"), 10);
            const view_type = url_hash.get("view_type");
            // Check if this is a shuttle-related page displaying a form view with proper record ID
            if (
                this._get_shuttle_models().indexOf(rec_model) !== -1 &&
                view_type === "form" &&
                !_.isUndefined(rec_id) &&
                rec_id > 0
            ) {
                // Display notifications only for the proper shuttle
                for (let i = 0; i < notifications.length; i++) {
                    const notif = notifications[i];
                    const shuttle_info = notif[1].params.shuttle_info;
                    if (shuttle_info[rec_model] === rec_id) {
                        filtered_notifications.push(notif);
                    }
                }
            }
            return filtered_notifications;
        },

        _get_shuttle_models: function () {
            return [
                "vertical.lift.shuttle",
                "vertical.lift.operation.inventory",
                "vertical.lift.operation.pick",
                "vertical.lift.operation.put",
            ];
        },
    });
});
