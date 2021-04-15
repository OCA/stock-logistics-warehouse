# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models


class MeasuringWizard(models.TransientModel):
    _inherit = "measuring.wizard"

    def get_measure(self):
        self.ensure_one()
        device = self.device_id._get_measuring_device()
        device.get_measure()


class MeasuringWizardLine(models.TransientModel):
    _inherit = "measuring.wizard.line"

    def measuring_select_for_measure(self):
        success = super().measuring_select_for_measure()
        if success:
            self.wizard_id.get_measure()
            self.packaging_id._measuring_device_release()
        return success
