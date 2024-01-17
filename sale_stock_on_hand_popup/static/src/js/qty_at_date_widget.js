odoo.define("sale_stock_on_hand_popup.QtyAtDateWidget", function (require) {
    "use strict";

    const QtyAtDateWidget = require("sale_stock.QtyAtDateWidget");

    QtyAtDateWidget.include({
        async _openStock(ev) {
            ev.stopPropagation();

            return this.trigger_up("button_clicked", {
                attrs: {
                    name: "action_open_quants_show_products",
                    type: "object",
                },
                record: this.data.product_id,
            });
        },

        _getContent() {
            const $content = this._super.apply(this, arguments);
            if ($content) {
                $content.on("click", ".action_open_stock", this._openStock.bind(this));
            }
            return $content;
        },
    });

    return QtyAtDateWidget;
});
