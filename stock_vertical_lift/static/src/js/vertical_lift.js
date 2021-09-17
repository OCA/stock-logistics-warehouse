odoo.define("stock_vertical_lift.vertical_lift", function (require) {
    "use strict";

    var KanbanRecord = require("web.KanbanRecord");
    var FormController = require("web.FormController");

    KanbanRecord.include({
        _openRecord: function () {
            if (
                this.modelName === "vertical.lift.shuttle" &&
                this.$el.hasClass("open_shuttle_screen")
            ) {
                var self = this;
                this._rpc({
                    method: "action_open_screen",
                    model: self.modelName,
                    args: [self.id],
                }).then(function (action) {
                    self.trigger_up("do_action", {action: action});
                });
            } else {
                this._super.apply(this, arguments);
            }
        },
    });

    FormController.include({
        init: function () {
            this._super.apply(this, arguments);
            if (this.modelName.startsWith("vertical.lift.operation.")) {
                this.call("bus_service", "addChannel", "notify_vertical_lift_screen");
                this.call(
                    "bus_service",
                    "on",
                    "notification",
                    this,
                    this.vlift_bus_notification
                );
                this.call("bus_service", "startPolling");
            }
        },
        vlift_bus_notification: function (notifications) {
            var self = this;
            _.each(notifications, function (notification) {
                var channel = notification[0];
                var message = notification[1];
                if (channel === "notify_vertical_lift_screen") {
                    switch (message.action) {
                        case "refresh":
                            self.vlift_bus_action_refresh(message.params);
                            break;
                    }
                }
            });
        },
        vlift_bus_action_refresh: function (params) {
            var selectedIds = this.getSelectedIds();
            if (!selectedIds.length) {
                return;
            }
            var currentId = selectedIds[0];
            if (params.id === currentId && params.model === this.modelName) {
                this.reload();
            }
        },
        destroy: function () {
            if (this.modelName.startsWith("vertical.lift.operation.")) {
                this.call(
                    "bus_service",
                    "deleteChannel",
                    "notify_vertical_lift_screen"
                );
            }
            this._super.apply(this, arguments);
        },
    });

    return {};
});
