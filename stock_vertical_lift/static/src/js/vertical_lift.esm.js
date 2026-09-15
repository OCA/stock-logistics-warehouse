/* global document, InputEvent */
import {
    Component,
    onMounted,
    onPatched,
    onWillUnmount,
    useRef,
    useState,
    xml,
} from "@odoo/owl";
import {BarcodeHandlerField} from "@barcodes/barcode_handler_field";
import {Dialog} from "@web/core/dialog/dialog";
import {FormController} from "@web/views/form/form_controller";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {Mutex} from "@web/core/utils/concurrency";
import {_t} from "@web/core/l10n/translation";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";
import {useHotkey} from "@web/core/hotkeys/hotkey_hook";
import {useService} from "@web/core/utils/hooks";

const OPERATION_MODEL_PREFIX = "vertical.lift.operation.";

const SWITCH_BARCODE_METHODS = {
    "OBTswitch-pick": "switch_pick",
    "OBTswitch-put": "switch_put",
    "OBTswitch-inventory": "switch_inventory",
};

// Button (OBT) and command (OCD) barcodes are handled by the generic
// handlers of the barcodes module, the operation must not receive them.
const ACTION_BARCODE_RE = /^(OBT|OCD)/;

// A scan must wait for the previous one to be processed and reloaded,
// otherwise two scans could be evaluated against the same operation step.
// record.update() had this queuing through the form model mutex.
const scanMutex = new Mutex();

function isOperationModel(resModel) {
    return resModel.startsWith(OPERATION_MODEL_PREFIX);
}

function blurActiveElement() {
    const el = document.activeElement;
    if (el && el !== document.body) {
        el.blur();
    }
}

// The scanner keys typed into the focused input stay in its value: remove
// them once the barcode service confirmed they were a barcode.
function stripScannedBarcode(ev) {
    const input = ev.target;
    const barcode = ev.detail.barcode;
    if (input.value.endsWith(barcode)) {
        input.value = input.value.slice(0, -barcode.length);
        input.dispatchEvent(new InputEvent("input", {bubbles: true}));
    }
}

// Barcode_service.js ignores keys typed while an <input> has the focus unless
// the input carries these attributes, so a scan would be lost.
function enableBarcodeOnInputs(root) {
    for (const input of root.querySelectorAll("input:not([barcode_events])")) {
        input.setAttribute("barcode_events", "true");
        input.dataset.enableBarcode = "true";
        input.addEventListener("barcode_scanned", stripScannedBarcode);
    }
}

patch(BarcodeHandlerField.prototype, {
    setup() {
        super.setup();
        this.ormService = useService("orm");
        this.actionService = useService("action");
    },
    async onBarcodeScanned(event) {
        const barcode = event.detail.barcode;
        const {resModel, resId} = this.props.record;
        // Intercept OBTswitch-* barcodes on vertical lift operation forms before
        // the standard barcode_handler forwards them to the model's
        // on_barcode_scanned (which would emit "No location found for barcode").
        const method = SWITCH_BARCODE_METHODS[barcode];
        if (method) {
            const action = await this.ormService.call(resModel, method, [resId]);
            if (action) {
                this.actionService.doAction(action);
            }
            return;
        }
        if (!isOperationModel(resModel)) {
            return super.onBarcodeScanned(event);
        }
        if (ACTION_BARCODE_RE.test(barcode)) {
            return;
        }
        // Plain RPC + reload instead of record.update(): an update marks the
        // form dirty and its pending values (state...) get auto-saved later.
        await scanMutex.exec(async () => {
            await this.ormService.call(resModel, "on_barcode_scanned", [
                resId,
                barcode,
            ]);
            await this.props.record.load();
        });
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
        if (isOperationModel(this.props.resModel)) {
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
            // Enter leaves the focused input (e.g. the inventory quantity).
            useHotkey("enter", () => blurActiveElement(), {
                bypassEditableProtection: true,
            });
            const enableBarcode = () => enableBarcodeOnInputs(this.rootRef.el);
            onMounted(enableBarcode);
            onPatched(enableBarcode);
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
