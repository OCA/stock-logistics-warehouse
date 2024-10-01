# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    product_selection = fields.Selection(
        selection_add=[("pos_categories", "Point of Sale Categories")],
        ondelete={"pos_categories": "set default"},
    )

    pos_categ_ids = fields.Many2many(
        "pos.category",
        string="Point of Sale Categories",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _prepare_inventory_filter(self):
        self.ensure_one()
        Product = self.env["product.product"]
        products = Product
        if self.product_selection == "pos_categories":
            all_category_ids = (
                self.env["pos.category"]
                .search([("id", "child_of", self.pos_categ_ids.ids)])
                .ids
            )
            products = Product.search([("pos_categ_id", "in", all_category_ids)])
        return products

    def _get_quants(self, locations):
        if self.product_selection == "pos_categories":
            all_category_ids = (
                self.env["pos.category"]
                .search([("id", "child_of", self.pos_categ_ids.ids)])
                .ids
            )
            products = self.env["product.product"].search(
                [("pos_categ_id", "in", all_category_ids)]
            )
            return self.env["stock.quant"].search([("product_id", "in", products.ids)])
        return super()._get_quants(locations)
