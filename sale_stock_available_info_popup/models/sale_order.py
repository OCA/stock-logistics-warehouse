# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    immediately_usable_qty_today = fields.Float(
        compute="_compute_immediately_usable_qty_today"
    )

    @api.depends(
        "product_id",
        "product_uom_qty",
        "scheduled_date",
        "order_id.date_order",
        "warehouse_id",
    )
    def _compute_immediately_usable_qty_today(self):
        qty_processed_per_product = defaultdict(lambda: 0)
        self.immediately_usable_qty_today = False
        for line in self.sorted(key=lambda r: r.sequence):
            if not line.display_qty_widget:
                continue
            product = line.product_id.with_context(
                to_date=line.scheduled_date, warehouse=line.warehouse_id.id
            )
            qty_processed = qty_processed_per_product[product.id]
            line.immediately_usable_qty_today = (
                product.immediately_usable_qty - qty_processed
            )
            qty_processed_per_product[product.id] += line.product_uom_qty
