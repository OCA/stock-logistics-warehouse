odoo.define("stock_measuring_device.measuring_wizard", function (require) {
    "use strict";

    var FormController = require("web.FormController");

    FormController.include({
        init: function () {
            this._super.apply(this, arguments);
            if (this.modelName === "measuring.wizard") {
                this.call(
                    "bus_service",
                    "addChannel",
                    "notify_measuring_wizard_screen"
                );
                this.call(
                    "bus_service",
                    "on",
                    "notification",
                    this,
                    this.measuring_wizard_bus_notification
                );
                this.call("bus_service", "startPolling");
            }
        },
        measuring_wizard_bus_notification: function (notifications) {
            var self = this;
            _.each(notifications, function (notification) {
                var channel = notification[0];
                var message = notification[1];
                if (channel === "notify_measuring_wizard_screen") {
                    if (message.action === "refresh") {
                        self.measuring_wizard_bus_action_refresh(message.params);
                    }
                }
            });
        },
        measuring_wizard_bus_action_refresh: function (params) {
            var selectedIds = this.getSelectedIds();
            if (!selectedIds.length || params.model !== this.modelName) {
                return;
            }
            var currentId = selectedIds[0];
            if (params.id === currentId) {
                this.reload();
            }
        },
        destroy: function () {
            if (this.modelName === "measuring.wizard") {
                this.call(
                    "bus_service",
                    "deleteChannel",
                    "notify_measuring_wizard_screen"
                );
            }
            this._super.apply(this, arguments);
        },
    });

    return {};
});
