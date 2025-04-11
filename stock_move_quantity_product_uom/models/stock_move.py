# Copyright 2025 ForgeFlow
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    quantity_product_uom = fields.Float(
        string="Quantity in Product UoM",
        compute="_compute_quantity_product_uom",
        store=True,
        help="Quantity, expressed in the default UoM of the product",
    )

    @api.depends("product_id", "product_uom", "quantity")
    def _compute_quantity_product_uom(self):
        for move in self:
            move.quantity_product_uom = move.product_uom._compute_quantity(
                move.quantity, move.product_id.uom_id, rounding_method="HALF-UP"
            )
