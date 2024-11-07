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
        # OVERRIDE: Allow the inventory user to set the last inventory date.
        # https://github.com/odoo/odoo/blob/534220ee/addons/stock/models/stock_quant.py#L775
        if (
            self.env.context.get("_stock_inventory_discrepancy")
            and len(values) == 1
            and "last_inventory_date" in values
            and self.user_has_groups(
                "stock_inventory_discrepancy.group_stock_inventory_validation"
            )
        ):
            self = self.sudo()
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
