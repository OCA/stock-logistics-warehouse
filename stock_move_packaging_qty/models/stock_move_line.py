# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models
from odoo.tools import float_round


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_packaging_id = fields.Many2one(
        related="move_id.product_packaging_id", readonly=True
    )
    product_packaging_qty_reserved = fields.Float(
        string="Reserved Pkg. Qty.",
        help="Product packaging quantity reserved.",
        compute="_compute_product_packaging_qty_reserved",
        store=True,
    )
    product_packaging_qty_done = fields.Float(
        string="Done Pkg. Qty.",
        help="Product packaging quantity done.",
    )

    @api.depends("product_packaging_id", "reserved_qty")
    def _compute_product_packaging_qty_reserved(self):
        """Get the quantity done in product packaging."""
        self.product_packaging_qty_reserved = False
        for line in self:
            if not line.product_packaging_id.qty:
                continue
            line.product_packaging_qty_reserved = float_round(
                line.reserved_qty / line.product_packaging_id.qty,
                precision_rounding=line.product_packaging_id.product_uom_id.rounding,
            )

    def _get_aggregated_properties(self, move_line=False, move=False):
        """Aggregate by product packaging too."""
        result = super()._get_aggregated_properties(move_line, move)
        pkg = result["move"].product_packaging_id
        result["product_packaging"] = pkg
        result["line_key"] += f"_{pkg.id}"
        return result

    def _get_aggregated_product_quantities(self, **kwargs):
        """Aggregate by product packaging too."""
        result = super()._get_aggregated_product_quantities(**kwargs)
        # Know all involved move lines, following upstream criteria
        all_lines = self.browse()
        processed_moves = all_lines.move_id
        if kwargs.get("except_package"):
            all_lines |= self - self.filtered("result_package_id")
        if not kwargs.get("strict"):
            moves = (self.picking_id | self.picking_id.backorder_ids).move_ids
            all_lines |= moves.move_line_ids | moves.move_line_nosuggest_ids
        # Aggregate product packaging quantities
        for move_line in all_lines:
            props = self._get_aggregated_properties(move_line)
            try:
                agg = result[props["line_key"]]
            except KeyError:
                continue  # Missing aggregation; nothing to do
            agg.setdefault("product_packaging_qty", 0.0)
            agg.setdefault("product_packaging_qty_done", 0.0)
            agg["product_packaging_qty_done"] += move_line.product_packaging_qty_done
            if move_line.move_id not in processed_moves:
                agg["product_packaging_qty"] += move_line.move_id.product_packaging_qty
                processed_moves |= move_line.move_id
        return result
