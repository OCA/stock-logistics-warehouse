import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {StockLotCatalogKanbanRecord} from "./kanban_record.esm";
import {useService} from "@web/core/utils/hooks";

export class StockLotCatalogKanbanRenderer extends KanbanRenderer {
    static template = "StockLotCatalogKanbanRenderer";
    static components = {
        ...KanbanRenderer.components,
        KanbanRecord: StockLotCatalogKanbanRecord,
    };

    setup() {
        super.setup();
        this.action = useService("action");
    }

    get createLotContext() {
        return {};
    }

    async createLot() {
        await this.action.doAction(
            {
                type: "ir.actions.act_window",
                res_model: "stock.lot",
                target: "new",
                views: [[false, "form"]],
                view_mode: "form",
                context: this.createLotContext,
            },
            {
                onClose: () => this.props.list.model.load(),
            }
        );
    }
}
