/** @odoo-module **/

import {registry} from "@web/core/registry";
import {systrayService} from "@base_tier_validation/js/systray_service.esm";

const serviceRegistry = registry.category("services");
serviceRegistry.add("review_systray_service", systrayService);
