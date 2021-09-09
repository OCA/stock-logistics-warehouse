odoo.define("stock_inventory_discrepancy.InventoryValidationController", function (
    require
) {
    "use strict";

    var core = require("web.core");
    var InventoryValidationController = require("stock.InventoryValidationController");

    var _t = core._t;

    InventoryValidationController.include({
        /**
         * @override
         * @see displayNotification
         */
        do_notify: function (title, message, sticky, className) {
            var self = this;
            if (this.modelName === "stock.inventory.line") {
                this._rpc({
                    model: "stock.inventory",
                    method: "read",
                    args: [this.inventory_id, ["state"]],
                })
                    .then(function (res) {
                        if (res[0].state === "pending") {
                            title = _t("Pending to Approve");
                            message = _t("The inventory needs to be approved");
                        }
                    })
                    .finally(function () {
                        return self.displayNotification({
                            type: "warning",
                            title: title,
                            message: message,
                            sticky: sticky,
                            className: className,
                        });
                    });
            }
        },
    });
});
