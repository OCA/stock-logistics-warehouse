/** @odoo-module **/

import {ListController} from "@web/views/list/list_controller";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class VlmRequestListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
    }
    async onClickVlmRequest() {
        const resIds = this.model.root.selection.map((record) => record.resId);
        const action = await this.orm.call(
            "stock.vlm.task",
            "action_do_tasks",
            [resIds],
            {}
        );
        this.action.doAction(action);
    }
}

registry.category("views").add("stock_vlm_task_action_tree", {
    ...listView,
    Controller: VlmRequestListController,
    buttonTemplate: "VlmTaskRequestListView.buttons",
});
