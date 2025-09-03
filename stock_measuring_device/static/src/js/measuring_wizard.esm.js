import {registry} from "@web/core/registry";

export const measuringWizardNotificationService = {
    dependencies: ["action", "bus_service", "orm"],
    start(env, {action, bus_service, orm}) {
        this.action = action;
        this.bus_service = bus_service;
        this.orm = orm;
        const self = this;
        this.bus_service.subscribe("notify_measuring_wizard_screen", (notification) => {
            self.notifyMeasuringWizardScreen(notification);
        });
        this.bus_service.start();
    },
    async notifyMeasuringWizardScreen(notification) {
        if (notification.action === "refresh") {
            await this.notifyMeasuringWizardScreenRefresh(notification.params.id);
        }
    },
    async notifyMeasuringWizardScreenRefresh(resId) {
        const refreshAction = await this.orm.call("measuring.wizard", "reload", [
            resId,
        ]);
        await this.action.doAction(refreshAction);
    },
};

registry
    .category("services")
    .add("measuringWizardNotificationService", measuringWizardNotificationService);
