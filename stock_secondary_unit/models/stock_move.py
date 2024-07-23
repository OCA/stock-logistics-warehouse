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

    @api.depends("product_id")
    def _compute_product_uom(self):
        res = super()._compute_product_uom()
        for move in self:
            move._onchange_helper_product_uom_for_secondary()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product = self.env["product.product"].browse(vals.get("product_id", False))
            if product:
                vals.update(
                    {
                        "secondary_uom_id": product.stock_secondary_uom_id.id
                        or product.product_tmpl_id.stock_secondary_uom_id.id,
                    }
                )
        return super().create(vals_list)

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
    _secondary_unit_fields = {"qty_field": "quantity", "uom_field": "product_uom_id"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            move = self.env["stock.move"].browse(vals.get("move_id", False))
            if move.secondary_uom_id:
                vals["secondary_uom_id"] = move.secondary_uom_id.id
        return super().create(vals_list)

    @api.depends("secondary_uom_id", "secondary_uom_qty", "quant_id")
    def _compute_quantity(self):
        self._compute_helper_target_field_qty()
