# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_packaging_id = fields.Many2one(
        related="move_id.product_packaging_id",
        readonly=True,
    )
    product_packaging_quantity = fields.Float(
        string="Done Packaging Quantity",
        compute="_compute_product_packaging_quantity",
        store=True,
        readonly=False,
        help="Quantity done in Product Packaging",
    )

    @api.depends(
        "picking_type_id", "move_id.product_packaging_id", "product_uom_id", "quantity"
    )
    def _compute_product_packaging_quantity(self):
        """Set product_packaging_quantity automatically."""
        auto_fill_ppq = self.filtered_domain(
            [
                ("picking_type_id.automatic_done_packaging_calculation", "=", True),
            ]
        )
        auto_fill_ppq.product_packaging_quantity = 0
        for line in auto_fill_ppq:
            if not line.move_id.product_packaging_id:
                continue
            # Same as product_packaging_qty at the first time
            line.product_packaging_quantity = (
                line.move_id.product_packaging_id._compute_qty(
                    line.quantity, line.product_uom_id
                )
            )
