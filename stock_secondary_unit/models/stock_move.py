# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = ["stock.move", "product.secondary.unit.mixin"]
    _name = "stock.move"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }

    product_uom_qty = fields.Float(
        store=True,
        readonly=False,
        compute="_compute_product_uom_qty",
        copy=True,
        precompute=True,
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_uom_qty(self):
        self._compute_helper_target_field_qty()

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        """Don't merge moves with distinct secondary units"""
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields += ["secondary_uom_id"]
        return distinct_fields

    def _prepare_extra_move_vals(self, qty):
        vals = super()._prepare_extra_move_vals(qty)
        if self.secondary_uom_id:
            vals["secondary_uom_id"] = self.secondary_uom_id.id
        return vals


class StockMoveLine(models.Model):
    _inherit = ["stock.move.line", "product.secondary.unit.mixin"]
    _name = "stock.move.line"
    _secondary_unit_fields = {"qty_field": "qty_done", "uom_field": "product_uom_id"}

    qty_done = fields.Float(
        store=True, readonly=False, compute="_compute_qty_done", precompute=True
    )

    @api.model
    def create(self, vals):
        move = self.env["stock.move"].browse(vals.get("move_id", False))
        if move.secondary_uom_id:
            vals["secondary_uom_id"] = move.secondary_uom_id.id
        return super().create(vals)

    @api.depends("secondary_uom_id", "secondary_uom_qty")
    def _compute_qty_done(self):
        self._compute_helper_target_field_qty()
