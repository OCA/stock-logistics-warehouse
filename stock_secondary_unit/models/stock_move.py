# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class StockMove(models.Model):
    _inherit = ["stock.move", "product.secondary.unit.mixin"]
    _name = "stock.move"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }

    product_uom_qty = fields.Float(
        store=True, readonly=False, compute="_compute_product_uom_qty", copy=True
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_uom_qty(self):
        self._compute_helper_target_field_qty()

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    def _merge_moves_fields(self):
        res = super()._merge_moves_fields()
        res["secondary_uom_qty"] = sum(self.mapped("secondary_uom_qty"))
        return res

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        """Don't merge moves with distinct secondary units"""
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields += ["secondary_uom_id"]
        return distinct_fields


class StockMoveLine(models.Model):
    _inherit = ["stock.move.line", "product.secondary.unit.mixin"]
    _name = "stock.move.line"
    _secondary_unit_fields = {"qty_field": "qty_done", "uom_field": "product_uom_id"}

    qty_done = fields.Float(store=True, readonly=False, compute="_compute_qty_done")

    @api.model
    def create(self, vals):
        move = self.env["stock.move"].browse(vals.get("move_id", False))
        if move.secondary_uom_id:
            uom = self.env["uom.uom"].browse(vals["product_uom_id"])
            factor = move.secondary_uom_id.factor * uom.factor
            move_line_qty = vals.get("product_uom_qty", vals.get("qty_done", 0.0))
            qty = float_round(
                move_line_qty / (factor or 1.0),
                precision_rounding=move.secondary_uom_id.uom_id.rounding,
            )
            vals.update(
                {"secondary_uom_qty": qty, "secondary_uom_id": move.secondary_uom_id.id}
            )
        return super().create(vals)

    @api.depends("secondary_uom_id", "secondary_uom_qty")
    def _compute_qty_done(self):
        self._compute_helper_target_field_qty()
