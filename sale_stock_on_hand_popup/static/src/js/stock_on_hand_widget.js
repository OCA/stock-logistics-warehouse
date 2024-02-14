odoo.define("sale_stock_on_hand_popup.StockOnHandWidget", function (require) {
    "use strict";

    var Widget = require("web.Widget");
    var widget_registry = require("web.widget_registry");

    var StockOnHandWidget = Widget.extend({
        template: "sale_stock_on_hand_popup.qtyOnHand",
        events: _.extend({}, Widget.prototype.events, {
            "click .fa-arrow-right": "_onClickButton",
        }),

        /**
         * @override
         * @param {Widget|null} parent
         * @param {Object} params
         */
        init: function (parent, params) {
            this.data = params.data;
            this.fields = params.fields;
            this._super(parent);
        },

        updateState: function (state) {
            var candidate = state.data[this.getParent().currentRow];
            if (candidate) {
                this.data = candidate.data;
                this.renderElement();
            }
        },

        _onClickButton: async function (ev) {
            ev.stopPropagation();
            var action = await this._rpc({
                model: "product.product",
                method: "action_open_quants_show_products",
                args: [[this.data.product_id.data.id]],
            });
            action.views = [[false, "form"]];
            return this.do_action(action);
        },
    });

    widget_registry.add("stock_on_hand_widget", StockOnHandWidget);

    return StockOnHandWidget;
});
