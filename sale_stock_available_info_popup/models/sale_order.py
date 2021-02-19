# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    immediately_usable_qty_today = fields.Float(
        compute="_compute_immediately_usable_qty_today"
    )

    @api.depends("product_id", "product_uom_qty")
    def _compute_immediately_usable_qty_today(self):
        qty_processed_per_product = defaultdict(lambda: 0)
        remaining = self.env["sale.order.line"]
        for line in self.sorted(key=lambda r: r.sequence):
            if not line.display_qty_widget:
                remaining |= line
                continue
            product = line.product_id
            qty_processed = qty_processed_per_product[product.id]
            line.immediately_usable_qty_today = (
                product.immediately_usable_qty - qty_processed
            )
            qty_processed_per_product[product.id] += line.product_uom_qty
        remaining.write({"immediately_usable_qty_today": False})
