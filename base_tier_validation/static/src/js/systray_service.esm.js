/** @odoo-module **/

import {ReviewerMenuContainer} from "./reviewer_menu_container.esm";

import {registry} from "@web/core/registry";

const systrayRegistry = registry.category("systray");

export const systrayService = {
    start() {
        systrayRegistry.add(
            "base_tier_validation.ReviewerMenu",
            {Component: ReviewerMenuContainer},
            {sequence: 99}
        );
    },
};
