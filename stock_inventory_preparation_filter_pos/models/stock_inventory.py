# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    pos_categ_ids = fields.Many2many(
        "pos.category",
        string="Point of Sale Categories",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.model
    def _selection_filter(self):
        res_filter = super()._selection_filter()
        res_filter.insert(
            -1, ("pos_categories", _("Selected Point of Sale Categories"))
        )
        return res_filter

    def _prepare_inventory_filter(self):
        products = super()._prepare_inventory_filter()
        if self.filter == "pos_categories":
            products = self.env["product.product"].search(
                [("pos_categ_id", "child_of", self.pos_categ_ids.ids)]
            )
        return products
