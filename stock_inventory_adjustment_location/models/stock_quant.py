# Copyright 2026 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_inventory_move_values(
        self,
        qty,
        location_id,
        location_dest_id,
        package_id=False,
        package_dest_id=False,
    ):
        ctx_loc = self.env.context.get("inventory_location_id")
        if ctx_loc:
            inv_location = self.env["stock.location"].browse(ctx_loc)
            if location_id.usage == "inventory":
                location_id = inv_location
            if location_dest_id.usage == "inventory":
                location_dest_id = inv_location
        return super()._get_inventory_move_values(
            qty,
            location_id,
            location_dest_id,
            package_id=package_id,
            package_dest_id=package_dest_id,
        )
