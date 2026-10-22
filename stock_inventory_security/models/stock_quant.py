# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    inventory_quantity_auto_apply = fields.Float(
        # Change stock.group_stock_manager to our own group.
        groups="stock_inventory_security.group_inventory_adjustment",
    )

    def user_has_groups(self, groups):
        # Most inventory adjustment operations are limited to users having
        # the Inventory Manager group.
        # OVERRIDE: Hijack the check to replace it with our own group.
        if groups == "stock.group_stock_manager" and self.env.context.get(
            "_stock_inventory_security"
        ):
            groups = "stock_inventory_security.group_inventory_adjustment"
        return super().user_has_groups(groups)

    def _get_quants_action(self, domain=None, extend=False):
        # OVERRIDE: Show the editable quants view for users having the Inventory
        # Adjustments group.
        # The original method would only do it for Stock Managers.
        if self.user_has_groups("stock_inventory_security.group_inventory_adjustment"):
            self = self.with_context(_stock_inventory_security=True)
        return super()._get_quants_action(domain=domain, extend=extend)

    def action_view_inventory(self):
        # OVERRIDE: Disable the "My count" filter for users having the Inventory
        # Adjustments group.
        if self.user_has_groups("stock_inventory_security.group_inventory_adjustment"):
            self = self.with_context(_stock_inventory_security=True)
        return super().action_view_inventory()

    def _apply_inventory(self):
        if self.user_has_groups("stock_inventory_security.group_inventory_adjustment"):
            self = self.with_context(_stock_inventory_security=True)
        return super()._apply_inventory()
