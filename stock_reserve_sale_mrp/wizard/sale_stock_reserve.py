# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.tools import float_is_zero


class SaleStockReserve(models.TransientModel):
    _inherit = "sale.stock.reserve"

    def _prepare_stock_reservation_bom_line(self, line, bom_line, bom_vals):
        self.ensure_one()
        vals = self._prepare_stock_reservation(line)
        vals.pop("price_unit", None)
        vals.update(
            {
                "product_id": bom_line.product_id.id,
                "product_uom": bom_line.product_uom_id.id,
                "product_uom_qty": bom_vals["qty"],
            }
        )
        return vals

    def _prepare_stock_reservation_vals_list(self, reserve_line):
        bom_kit = reserve_line._get_kit_bom()
        if not bom_kit:
            return super()._prepare_stock_reservation_vals_list(reserve_line)
        self.ensure_one()
        qty = reserve_line.product_uom._compute_quantity(
            reserve_line.quantity, bom_kit.product_uom_id, round=False
        )
        qty_to_produce = qty / bom_kit.product_qty
        __, bom_sub_lines = bom_kit.explode(reserve_line.product_id, qty_to_produce)
        return [
            self._prepare_stock_reservation_bom_line(
                reserve_line.sale_line_id, bom_line, bom_vals
            )
            for bom_line, bom_vals in bom_sub_lines
            if bom_line.product_id.type in ("product", "consu")
            and not float_is_zero(
                bom_vals["qty"], precision_rounding=bom_line.product_uom_id.rounding
            )
        ]
