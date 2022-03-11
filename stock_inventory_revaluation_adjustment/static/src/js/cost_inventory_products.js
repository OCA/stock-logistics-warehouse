odoo.define("stock_inventory_revaluation_adjustment.ListView", function (require) {
    "use strict";
    var ListController = require("web.ListController");
    ListController.include({
        renderButtons: function ($node) {
            var self = this;
            var rec = this._super($node);
            self.$buttons.on("click", ".add_multi_product_adjustment", function () {
                self._importdoctorClick(this);
            });
            return rec;
        },
        _importdoctorClick: function () {
            var self = this;
            self.do_action(
                {
                    name: "Products",
                    type: "ir.actions.act_window",
                    res_model: "stock.add.multi.product",
                    view_mode: "form",
                    views: [[false, "form"]],
                    target: "new",
                    context: self.model.loadParams.context,
                },
                {
                    on_close: function () {
                        return self.trigger_up("reload");
                    },
                }
            );
        },
    });
});
