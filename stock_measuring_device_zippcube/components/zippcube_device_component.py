# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ZippcubeDevice(Component):
    _name = "device.component.zippcube"
    _inherit = "measuring.device.base"
    _usage = "zippcube"

    def preprocess_measures(self, measures):
        weight_keys = ("weight",)
        measures_keys = ("length", "width", "height")
        data = {}
        for key in weight_keys + measures_keys:
            value = measures[key]
            if isinstance(value, str):
                value = float(value.replace(",", "."))
            if key in measures_keys:
                # lengths are in cm -> convert to mm
                value *= 10
            data[key] = value
        return {
            "max_weight": data["weight"],
            "packaging_length": data["length"],
            "width": data["width"],
            "height": data["height"],
        }

    def post_update_packaging_measures(self, measures, packaging, wizard_line):
        # wizard_line is only set when measurements are made from the measurement
        # device wizard.
        if wizard_line:
            wizard_line.wizard_id._send_notification_refresh()
        packaging._measuring_device_release()
