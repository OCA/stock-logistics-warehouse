# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleStockReserve(models.TransientModel):
    _inherit = "sale.stock.reserve"

    def _prepare_stock_reservation_bom_line(self, line, bom_line, bom_vals):
        self.ensure_one()
        return {
            "product_id": bom_line.product_id.id,
            "product_uom": bom_line.bom_id.product_uom_id.id,
            "product_uom_qty": bom_vals["qty"],
            "date_validity": self.date_validity,
            "name": "{} ({})".format(line.order_id.name, line.name),
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "note": self.note,
            "sale_line_id": line.id,
            "restrict_partner_id": self.owner_id.id,
        }

    def stock_reserve(self, line_ids):
        self.ensure_one()
        lines = self.env["sale.order.line"].browse(line_ids)
        lines_without_kit = self.env["sale.order.line"]
        vals_list = []
        for line in lines:
            bom_kit = self.env["mrp.bom"]._bom_find(
                product=line.product_id,
                company_id=line.company_id.id,
                bom_type="phantom",
            )
            if not bom_kit:
                lines_without_kit |= line
            else:
                qty = line.product_uom._compute_quantity(
                    line.product_uom_qty, bom_kit.product_uom_id, round=False
                )
                qty_to_produce = qty / bom_kit.product_qty
                boms, bom_sub_lines = bom_kit.explode(line.product_id, qty_to_produce)
                for bom_line, bom_vals in bom_sub_lines:
                    vals_list.append(
                        self._prepare_stock_reservation_bom_line(
                            line, bom_line, bom_vals
                        )
                    )
        if vals_list:
            reserves = self.env["stock.reservation"].create(vals_list)
            reserves.reserve()
        return super().stock_reserve(lines_without_kit.ids)
