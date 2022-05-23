odoo.define("stock_request_kanban.StockRequestKanbanController", function (require) {
    "use strict";

    var core = require("web.core");
    var ListController = require("web.ListController");

    var qweb = core.qweb;

    var StockRequestKanbanController = ListController.extend({
        // -------------------------------------------------------------------------
        // Public
        // -------------------------------------------------------------------------

        init: function (parent, model, renderer) {
            this.context = renderer.state.getContext();
            return this._super.apply(this, arguments);
        },

        /**
         * @override
         */

        renderButtons: function () {
            this._super.apply(this, arguments);
            var $buttonScan = $(qweb.render("StockRequestKanban.Buttons"));
            $buttonScan.on("click", this._onOpenWizard.bind(this));

            this.$buttons.prepend($buttonScan);
        },

        // -------------------------------------------------------------------------
        // Handlers
        // -------------------------------------------------------------------------

        _onOpenWizard: function () {
            var context = {
                active_model: this.modelName,
            };
            this.do_action({
                res_model: "wizard.stock.request.kanban",
                views: [[false, "form"]],
                target: "new",
                type: "ir.actions.act_window",
                context: context,
            });
        },
    });

    return StockRequestKanbanController;
});
