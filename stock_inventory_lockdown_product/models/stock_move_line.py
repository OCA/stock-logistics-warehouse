# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.constrains("location_dest_id", "location_id", "state")
    def _check_locked_location(self):
        soft_lock_lines = self.filtered(
            lambda ml: ml.company_id.use_soft_inventory_lock
        )
        for move_line in soft_lock_lines:
            if move_line.state == "done":
                inventories = self.env[
                    "stock.inventory"
                ]._get_open_inventories_by_locations(
                    [move_line.location_dest_id.id, move_line.location_id.id]
                )
                for inventory in inventories:
                    inventory_products = inventory.stock_quant_ids.mapped(
                        "product_id.id"
                    )
                    if move_line.product_id.id in inventory_products:
                        if (
                            not move_line.location_dest_id.usage == "inventory"
                            or not move_line.location_id.usage == "inventory"
                        ):
                            location_names = inventory.location_ids.mapped(
                                "complete_name"
                            )
                            msg = self.env._(
                                "Inventory adjustment underway at the following "
                                "location(s):\n- %(locations)s\n"
                                "Product '%(product)s' is included in the inventory. "
                                "Moving it to/from these locations is not"
                                " allowed until the adjustment is complete."
                            )
                            raise ValidationError(
                                msg
                                % {
                                    "locations": "\n - ".join(location_names),
                                    "product": move_line.product_id.display_name,
                                }
                            )
        no_soft_lock_lines = self - soft_lock_lines
        if no_soft_lock_lines:
            return super(StockMoveLine, no_soft_lock_lines)._check_locked_location()
