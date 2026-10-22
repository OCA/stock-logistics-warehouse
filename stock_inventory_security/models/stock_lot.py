# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def user_has_groups(self, groups):
        # Most inventory adjustment operations are limited to users having
        # the Inventory Manager group.
        # OVERRIDE: Hijack the check to replace it with our own group.)
        if groups == "stock.group_stock_manager" and self.env.context.get(
            "_stock_inventory_security"
        ):
            groups = "stock_inventory_security.group_inventory_adjustment"
        return super().user_has_groups(groups)

    def action_lot_open_quants(self):
        # OVERRIDE: Add the inventory_mode context
        if self.user_has_groups("stock_inventory_security.group_inventory_adjustment"):
            self = self.with_context(_stock_inventory_security=True)
        return super().action_lot_open_quants()
