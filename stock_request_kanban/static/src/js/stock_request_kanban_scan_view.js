odoo.define("stock_request_kanban.StockRequestKanbanListView", function (require) {
    "use strict";

    var ListView = require("web.ListView");
    var StockRequestKanbanController = require("stock_request_kanban.StockRequestKanbanController");
    var viewRegistry = require("web.view_registry");

    var StockRequestKanbanListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: StockRequestKanbanController,
        }),
    });

    viewRegistry.add("stock_request_kanban_list", StockRequestKanbanListView);

    return StockRequestKanbanListView;
});
