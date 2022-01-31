# Copyright 2018-20 ForgeFlow <http://www.forgeflow.com>

from odoo import _, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_update_quantity_on_inventory_adjustment(self):
        """Create an Inventory Adjustment instead of edit directly on quants"""
        self.ensure_one()
        view_form_id = self.env.ref("stock.view_inventory_form").id
        xmlid = "stock.action_inventory_form"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "views": [(view_form_id, "form")],
                "view_mode": "form",
                "context": {
                    "default_product_ids": [(6, 0, self.product_variant_ids.ids)],
                    "default_name": _("%s: Inventory Adjustment") % self.display_name,
                },
            }
        )
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_update_quantity_on_inventory_adjustment(self):
        """Create an Inventory Adjustment instead of edit directly on quants"""
        self.ensure_one()
        view_form_id = self.env.ref("stock.view_inventory_form").id
        xmlid = "stock.action_inventory_form"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "views": [(view_form_id, "form")],
                "view_mode": "form",
                "context": {
                    "default_product_ids": [(6, 0, [self.id])],
                    "default_name": _("%s: Inventory Adjustment") % self.display_name,
                },
            }
        )
        return action
