# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    measuring_device_id = fields.Many2one(
        "measuring.device",
        copy=False,
        string="Measuring device which will scan the package",
        help="Technical field set when an operator uses the device "
        "to scan this package",
    )

    def _measuring_device_assign(self, device):
        """Assign the measuring device to the current product packaging"""
        # self can be an empty recordset, for the unit line which updates the
        # product info
        if self:
            self.measuring_device_id = device

    def _measuring_device_release(self):
        """Free the measuring device from the current product packaging"""
        # self can be an empty recordset, for the unit line which updates the
        # product info
        if self:
            self.measuring_device_id = False

    def _measuring_device_find_assigned(self, device):
        """search packaging being assigned to the specified device"""
        packaging = self.search(
            [("measuring_device_id", "=", device.id)], order="write_date DESC", limit=2
        )
        if len(packaging) > 1:
            warning_msg = _(
                "Several packagings ({}) found to update by "
                "device {}. Will update the first: {}".format(
                    packaging, self.name, packaging[0]
                )
            )
            _logger.warning(warning_msg)
            packaging = packaging[0]
        return packaging
