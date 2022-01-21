/** @odoo-module **/

import ListView from "web.ListView";
import StockRequestKanbanController from "@stock_request_kanban/js/stock_request_kanban_scan_controller.esm";
import viewRegistry from "web.view_registry";

var StockRequestKanbanListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: StockRequestKanbanController,
    }),
});

viewRegistry.add("stock_request_kanban_list", StockRequestKanbanListView);

export default StockRequestKanbanListView;
