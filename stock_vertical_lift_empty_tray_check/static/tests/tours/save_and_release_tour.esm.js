/* Copyright 2026 Camptocamp SA
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";

const EMPTY_CHECK_POPUP = ".modal button[name=button_confirm_empty]";

function delay(ms) {
    return new Promise((resolve) => browser.setTimeout(resolve, ms));
}

function findComponent(node, predicate) {
    if (predicate(node.component)) {
        return node.component;
    }
    for (const child of Object.values(node.children)) {
        const found = findComponent(child, predicate);
        if (found) {
            return found;
        }
    }
    return null;
}

registry
    .category("web_tour.tours")
    .add("vertical_lift_empty_tray_check_popup_refresh", {
        steps: () => [
            {
                content: "Click Save & Release",
                trigger: "button[name=button_save_and_release]",
                run: "click",
            },
            {
                content: "The 'Is the tray empty?' popup is displayed",
                trigger: EMPTY_CHECK_POPUP,
            },
            {
                content: "Receive a refresh notification for the pick screen",
                trigger: EMPTY_CHECK_POPUP,
                async run() {
                    // Bus notifications are not delivered in tests: call the
                    // handler the bus subscription calls.
                    const screen = findComponent(
                        odoo.__WOWL_DEBUG__.root.__owl__,
                        (c) =>
                            c?.vlift_bus_action_refresh &&
                            c.props.resModel === "vertical.lift.operation.pick"
                    );
                    screen.vlift_bus_action_refresh({
                        id: screen.props.resId,
                        model: screen.props.resModel,
                    });
                    await delay(1000);
                },
            },
            {
                content: "The popup is still displayed",
                trigger: EMPTY_CHECK_POPUP,
            },
        ],
    });
