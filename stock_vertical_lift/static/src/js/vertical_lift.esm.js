import {Component, onMounted, onWillUnmount, useRef, useState, xml} from "@odoo/owl";
import {BarcodeHandlerField} from "@barcodes/barcode_handler_field";
import {Dialog} from "@web/core/dialog/dialog";
import {FormController} from "@web/views/form/form_controller";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {_t} from "@web/core/l10n/translation";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const SWITCH_BARCODE_METHODS = {
    "OBTswitch-pick": "switch_pick",
    "OBTswitch-put": "switch_put",
    "OBTswitch-inventory": "switch_inventory",
};

// Intercept OBTswitch-* barcodes on vertical lift operation forms before the
// standard barcode_handler forwards them to the model's on_barcode_scanned
// (which would emit "No location found for barcode ...").
patch(BarcodeHandlerField.prototype, {
    setup() {
        super.setup();
        this.ormService = useService("orm");
        this.actionService = useService("action");
    },
    async onBarcodeScanned(event) {
        const barcode = event.detail.barcode;
        const method = SWITCH_BARCODE_METHODS[barcode];
        if (!method) {
            return super.onBarcodeScanned(event);
        }
        const {resModel, resId} = this.props.record;
        const action = await this.ormService.call(resModel, method, [resId]);
        if (action) {
            this.actionService.doAction(action);
        }
    },
});

patch(KanbanController.prototype, {
    async openRecord(record, mode) {
        if (
            record.resModel === "vertical.lift.shuttle" &&
            this.props.className.includes("open_shuttle_screen")
        ) {
            const ormService = this.env.services.orm;
            const action = await ormService.call(
                "vertical.lift.shuttle",
                "action_open_screen",
                [record.resId]
            );
            this.actionService.doAction(action);
        } else {
            super.openRecord(record, mode);
        }
    },
});

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.busService = useService("bus_service");
        if (this.props.resModel.startsWith("vertical.lift.operation.")) {
            this.busService.addChannel("notify_vertical_lift_screen");
            this.busService.addEventListener("notification", (notifications) => {
                notifications.forEach(([channel, message]) => {
                    if (
                        channel === "notify_vertical_lift_screen" &&
                        message.action === "refresh"
                    ) {
                        this.vlift_bus_action_refresh(message.params);
                    }
                });
            });
        }

        onWillUnmount(() => {
            this.busService.deleteChannel("notify_vertical_lift_screen");
        });
    },

    vlift_bus_action_refresh(params) {
        if (params.id === this.props.resId && params.model === this.props.resModel) {
            this.model.root.load();
        }
    },
});

// Manual barcode popup: emits a barcode_scanned event on the global barcode
// service bus, exactly like a real scanner, so the standard handlers and the
// patched BarcodeHandlerField above pick it up.
class ManualBarcodeDialog extends Component {
    static template = xml`
        <Dialog size="'sm'" title="title">
            <div class="o_vlift_shuttle_popup">
                <input
                    type="text"
                    class="form-control"
                    t-ref="input"
                    t-model="state.barcode"
                    t-on-keydown="onKeydown"
                />
            </div>
            <t t-set-slot="footer">
                <button class="btn btn-primary" t-on-click="onConfirm">Confirm</button>
                <button class="btn btn-secondary" t-on-click="props.close">Cancel</button>
            </t>
        </Dialog>
    `;
    static components = {Dialog};
    static props = {close: Function};

    setup() {
        this.title = _t("Barcode");
        this.state = useState({barcode: ""});
        this.barcodeService = useService("barcode");
        this.inputRef = useRef("input");
        onMounted(() => this.inputRef.el?.focus());
    }

    onKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.onConfirm();
        }
    }

    onConfirm() {
        const barcode = this.state.barcode.trim();
        // NOTE: We must ensure that the event is triggered after the props closes
        // So that events like `OBTsave` are correctly handled
        this.props.close();
        if (barcode) {
            browser.setTimeout(() => {
                this.barcodeService.bus.trigger("barcode_scanned", {barcode});
            }, 0);
        }
    }
}

registry.category("actions").add("vertical_lift_manual_barcode", (env) => {
    env.services.dialog.add(ManualBarcodeDialog);
});
