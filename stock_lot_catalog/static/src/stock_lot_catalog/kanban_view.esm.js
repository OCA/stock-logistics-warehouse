import {StockLotCatalogKanbanController} from "./kanban_controller.esm";
import {StockLotCatalogKanbanModel} from "./kanban_model.esm";
import {StockLotCatalogKanbanRenderer} from "./kanban_renderer.esm";
import {StockLotCatalogSearchPanel} from "./search/search_panel.esm";

import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

export const stockLotCatalogKanbanView = {
    ...kanbanView,
    Controller: StockLotCatalogKanbanController,
    Model: StockLotCatalogKanbanModel,
    Renderer: StockLotCatalogKanbanRenderer,
    SearchPanel: StockLotCatalogSearchPanel,
};

registry.category("views").add("stock_lot_kanban_catalog", stockLotCatalogKanbanView);
