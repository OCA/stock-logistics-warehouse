odoo.define("crm.leads.tree", function (require) {
    "use strict";
    const ListController = require("web.ListController");
    const ListView = require("web.ListView");
    const viewRegistry = require("web.view_registry");
    const core = require("web.core");
    const qweb = core.qweb;

    function renderVlmTasksActionButton() {
        if (this.$buttons) {
            this.$buttons.on("click", ".o_button_perform_vlm_tasks", async () => {
                const resIds = await this.getSelectedIdsWithDomain();
                this._rpc({
                    model: "stock.vlm.task",
                    method: "action_do_tasks",
                    args: [resIds],
                }).then((action) => {
                    this.do_action(action);
                });
            });
        }
    }

    var VlmTaskRequestListController = ListController.extend({
        _updateSelectionBox: function () {
            this._super.apply(this, arguments);
            if (this.$performTasksButtons) {
                this.$performTasksButtons.remove();
                this.$performTasksButtons = null;
            }
            this.$performTasksButtons = $(
                qweb.render("VlmTaskAction.perform_vlm_tasks_button")
            );
            if (this.$selectionBox) {
                this.$performTasksButtons.insertAfter(this.$selectionBox);
                renderVlmTasksActionButton.apply(this, arguments);
            }
        },
    });

    var VlmTaskRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: VlmTaskRequestListController,
        }),
    });

    viewRegistry.add("stock_vlm_task_action_tree", VlmTaskRequestListView);
});
