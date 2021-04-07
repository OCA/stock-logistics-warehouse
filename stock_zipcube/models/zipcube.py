# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ZipcubeDevice(models.Model):
    _inherit = "cubiscan.device"

    driver = fields.Selection(selection_add=[("zipcube", "Zipcube")])

    def _update_packaging_measures(self, measures):
        self.ensure_one()
        packaging = self.env["product.packaging"].search(
            [("scan_device_id", "=", self.id)], order="write_date DESC"
        )
        if len(packaging) == 0:
            _logger.error("Could not find packaging to update by device %s", self)
            raise UserError(_("No package found pending a scan by this device"))
        elif len(packaging) > 1:
            _logger.warning(
                "Several packagings (%s) found to update by device %s", packaging, self
            )
            _logger.warning("Will update the 1st %s", packaging[0])
        to_update = packaging[0]
        wizard_line = self.env["cubiscan.wizard.line"].search(
            [
                ("packaging_id", "=", to_update.id),
                ("wizard_id.device_id", "=", self.id),
            ],
            order="write_date DESC",
            limit=1,
        )
        if not wizard_line:
            _logger.warning("no wizard line found for this measure")
        wizard_line.write(
            {
                "lngth": measures["length"],
                "width": measures["width"],
                "height": measures["height"],
                "max_weight": measures["weight"],
            }
        )
        packaging.write({"scan_device_id": False})

        # Shows a message to the user that created the wizard, indicating
        # that the button 'refresh' must be pressed. We can't use the user
        # set in the current environment because the user that attends the
        # screen (that opened the wizard, thus created it) may be not the
        # same than the one (artificial user) that scans and submits the
        # data, e.g. by using an api call via a controller. We have to send
        # this original user in the environment because notify_warning checks
        # that you only notify a user which is the same than the one set in
        # the environment.
        # wizard_line.wizard_id.create_uid.with_user(
        #     wizard_line.wizard_id.create_uid.id
        # ).notify_warning(message=_("Please, press the REFRESH button."))
        _logger.warning(_("Please, press the REFRESH button."))
        return to_update
