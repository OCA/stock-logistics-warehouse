# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def write(self, vals):
        # OVERRIDE: Allow the inventory user to set the last inventory date.
        # https://github.com/odoo/odoo/blob/534220ee/addons/stock/models/stock_quant.py#L775
        if (
            self.env.context.get("_stock_inventory_security")
            and len(vals) == 1
            and "last_inventory_date" in vals
            and self.user_has_groups(
                "stock_inventory_security.group_inventory_adjustment"
            )
        ):
            self = self.sudo()
        return super().write(vals)
