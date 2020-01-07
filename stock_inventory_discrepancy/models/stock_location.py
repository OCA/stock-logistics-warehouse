# Copyright 2017-2020 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    discrepancy_threshold = fields.Float(
        string="Maximum Discrepancy Rate Threshold",
        digits=(3, 2),
        help="Maximum Discrepancy Rate allowed for any product when doing "
        "an Inventory Adjustment. Thresholds defined in Locations have "
        "preference over Warehouse's ones.",
    )
    propagate_discrepancy_threshold = fields.Boolean(
        string="Propagate discrepancy threshold",
        help="Propagate Maximum Discrepancy Rate Threshold to child locations",
    )

    def write(self, values):
        res = super().write(values)
        # Set the discrepancy threshold for all child locations
        if values.get("discrepancy_threshold", False):
            for location in self.filtered(
                lambda loc: loc.propagate_discrepancy_threshold and loc.child_ids
            ):
                location.child_ids.write(
                    {
                        "discrepancy_threshold": values["discrepancy_threshold"],
                        "propagate_discrepancy_threshold": True,
                    }
                )
        return res
