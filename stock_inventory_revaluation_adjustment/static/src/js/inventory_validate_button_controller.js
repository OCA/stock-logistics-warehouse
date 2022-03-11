odoo.define("product_cost_adjustment.CostAdjustmentValidationController", function (
    require
) {
    "use strict";

    var core = require("web.core");
    var ListController = require("web.ListController");

    var _t = core._t;
    var qweb = core.qweb;

    var CostAdjustmentValidationController = ListController.extend({
        events: _.extend(
            {
                "click .o_button_validate_cost_adjustment": "_onValidateCostAdjustment",
            },
            ListController.prototype.events
        ),

        /**
         * @override
         */
        init: function (parent, model, renderer) {
            var context = renderer.state.getContext();
            this.cost_adjustment_id = context.active_id;
            return this._super.apply(this, arguments);
        },

        // -------------------------------------------------------------------------
        // Public
        // -------------------------------------------------------------------------

        /**
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            var $validationButton = $(qweb.render("CostAdjustmentLines.Buttons"));
            this.$buttons.prepend($validationButton);
        },

        // -------------------------------------------------------------------------
        // Handlers
        // -------------------------------------------------------------------------

        /**
         * Handler called when user click on validation button in cost adjustment lines
         * view. Makes an rpc to try to validate the cost adjustment, then will go back on
         * the cost adjustment view form if it was validated.
         * This method could also open a wizard in case something was missing.
         *
         * @private
         */
        _onValidateCostAdjustment: function () {
            var self = this;
            var prom = Promise.resolve();
            var recordID = this.renderer.getEditableRecordID();
            if (recordID) {
                // If user's editing a record, we wait to save it before to try to
                // validate the cost adjustment.
                prom = this.saveRecord(recordID);
            }

            prom.then(function () {
                self._rpc({
                    model: "stock.cost.adjustment",
                    method: "action_validate",
                    args: [self.cost_adjustment_id],
                }).then(function (res) {
                    var exitCallback = function (infos) {
                        // In case we discarded a wizard, we do nothing to stay on
                        // the same view...
                        if (infos && infos.special) {
                            return;
                        }
                        // ... but in any other cases, we go back on the cost adjustment form.
                        self.do_notify(
                            false,
                            _t("The cost adjustment has been validated")
                        );
                        self.trigger_up("history_back");
                    };

                    if (_.isObject(res)) {
                        self.do_action(res, {on_close: exitCallback});
                    } else {
                        return exitCallback();
                    }
                });
            });
        },
    });

    return CostAdjustmentValidationController;
});
