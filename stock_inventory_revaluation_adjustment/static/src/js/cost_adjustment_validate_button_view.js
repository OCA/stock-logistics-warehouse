odoo.define("product_cost_adjustment.CostAdjustmentValidationView", function (require) {
    "use strict";

    var CostAdjustmentValidationController = require("product_cost_adjustment.CostAdjustmentValidationController");
    var ListView = require("web.ListView");
    var viewRegistry = require("web.view_registry");

    var CostAdjustmentValidationView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: CostAdjustmentValidationController,
        }),
    });

    viewRegistry.add("cost_adjustment_validate_button", CostAdjustmentValidationView);
});
