# Copyright 2018-24 ForgeFlow <http://www.forgeflow.com>

from odoo import _, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_update_quantity_on_inventory_adjustment(self):
        """Create an Inventory Adjustment instead of edit directly on quants"""
        self.ensure_one()
        view_id = self.env.ref("stock.view_stock_quant_tree_inventory_editable").id
        action = {
            "name": _("Update Quantity"),
            "type": "ir.actions.act_window",
            "res_model": "stock.quant",
            "views": [(view_id, "tree")],
            "view_mode": "tree",
            "context": {
                "default_product_ids": [(6, 0, self.product_variant_ids.ids)],
                "default_name": _("%s: Inventory Adjustment") % self.display_name,
            },
            "domain": [("product_id", "=", self.product_variant_ids.ids)],
        }
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_update_quantity_on_inventory_adjustment(self):
        """Create an Inventory Adjustment instead of edit directly on quants"""
        self.ensure_one()
        view_id = self.env.ref("stock.view_stock_quant_tree_inventory_editable").id
        action = {
            "name": _("Update Quantity"),
            "type": "ir.actions.act_window",
            "res_model": "stock.quant",
            "views": [(view_id, "tree")],
            "view_mode": "tree",
            "context": {
                "default_product_ids": [(6, 0, [self.id])],
                "default_name": _("%s: Inventory Adjustment") % self.display_name,
            },
            "domain": [("product_id", "=", self.id)],
        }
        return action
