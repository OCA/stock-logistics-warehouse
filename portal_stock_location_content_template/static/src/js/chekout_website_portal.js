odoo.define("portal_stock_location_content_template.checkout_website_portal", function (
    require
) {
    "use strict";

    const ajax = require("web.ajax");
    var publicWidget = require("web.public.widget");
    require("web.dom_ready");

    publicWidget.registry.Checkout = publicWidget.Widget.extend({
        selector: ".card",
        events: {
            "click #complete_checkout": "_onClickComplete",
            "change #counted_qty": "_onChangeCountedQty",
        },
        _onChangeCountedQty: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var expectedQty = $(ev.currentTarget)
                .parents("tr")
                .find("#expected_qty")
                .text();
            var countedQty = $(ev.currentTarget).val();
            if (expectedQty || countedQty) {
                var replenishedQty = expectedQty - countedQty;
                $(ev.currentTarget)
                    .parents("tr")
                    .find("#replenished_qty")
                    .val(replenishedQty);
            }
        },
        _onClickComplete: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            var lineVals = [];
            this.$(".checkout_lines tr").each(function (index, line) {
                var lineId = $(line).data("id");

                var countedValue = $(line).find("#counted_qty").val() || 0;
                var replenishedValue = $(line).find("#replenished_qty").val() || 0;
                lineVals.push({
                    id: lineId,
                    counted_qty: countedValue,
                    replenished_qty: replenishedValue,
                });
            });

            if (lineVals.length) {
                ajax.jsonRpc("/checkout/complete", "call", {
                    vals: lineVals,
                    stock_content: self.$("#checkout-table").data("checkout-id"),
                }).then((res) => {
                    if (res) {
                        window.location.href = "/my/checkouts";
                    }
                });
            }
        },
    });
});
