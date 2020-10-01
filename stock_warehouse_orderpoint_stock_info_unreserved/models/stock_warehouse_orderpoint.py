# Copyright 2018 Camptocamp SA
# Copyright 2016 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    product_location_qty_available_not_res = fields.Float(
        string="Quantity On Location (Unreserved)",
        compute="_compute_product_available_qty",
    )

    def _compute_product_available_qty(self):
        super()._compute_product_available_qty()
        op_by_loc = defaultdict(set)
        for order in self:
            op_by_loc[order.location_id].add(order.id)
        for location_id, order_in_loc in op_by_loc.items():
            order_in_loc = self.browse(order_in_loc)
            products = (
                order_in_loc.mapped("product_id")
                .with_context(location=location_id.id)
                ._compute_qty_available_not_reserved()
            )
            for order in order_in_loc:
                product = products[order.product_id.id]
                order.product_location_qty_available_not_res = product[
                    "qty_available_not_res"
                ]
