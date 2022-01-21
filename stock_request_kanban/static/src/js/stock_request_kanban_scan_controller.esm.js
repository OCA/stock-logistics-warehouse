/** @odoo-module **/

import ListController from "web.ListController";
import core from "web.core";

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

export default StockRequestKanbanController;
