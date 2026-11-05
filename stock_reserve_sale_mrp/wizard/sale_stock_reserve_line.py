# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from odoo import models
from odoo.tools import float_is_zero, float_round


class SaleStockReserveLine(models.TransientModel):
    _inherit = "sale.stock.reserve.line"

    def _get_kit_bom(self):
        self.ensure_one()
        return self.env["mrp.bom"]._bom_find(
            self.product_id,
            company_id=self.sale_line_id.company_id.id,
            bom_type="phantom",
        )[self.product_id]

    def _get_available_quantity(self):
        self.ensure_one()
        bom_kit = self._get_kit_bom()
        location = self.wizard_id.location_id
        if not bom_kit or not location or location.should_bypass_reservation():
            return super()._get_available_quantity()
        __, bom_sub_lines = bom_kit.explode(self.product_id, 1)
        qty_per_kit = defaultdict(float)
        for bom_line, bom_vals in bom_sub_lines:
            component = bom_line.product_id
            if component.type != "product" or float_is_zero(
                bom_vals["qty"], precision_rounding=bom_line.product_uom_id.rounding
            ):
                continue
            qty_per_kit[component] += bom_line.product_uom_id._compute_quantity(
                bom_vals["qty"] / bom_vals["original_qty"],
                component.uom_id,
                round=False,
                raise_if_failure=False,
            )
        ratios = [
            float_round(
                self.env["stock.quant"]._get_available_quantity(component, location)
                / qty,
                precision_rounding=component.uom_id.rounding,
                rounding_method="DOWN",
            )
            for component, qty in qty_per_kit.items()
            if qty
        ]
        if not ratios:
            return self.product_uom_qty
        kit_qty = (
            float_round(
                min(ratios) * bom_kit.product_qty,
                precision_rounding=bom_kit.product_uom_id.rounding,
            )
            // 1
        )
        return bom_kit.product_uom_id._compute_quantity(
            kit_qty, self.product_uom, rounding_method="DOWN"
        )
