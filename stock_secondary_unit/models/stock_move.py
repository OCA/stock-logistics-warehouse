# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class StockSecondaryUnitMixin(models.AbstractModel):
    _name = "stock.secondary.unit.mixin"
    _description = "Stock Secondary Unit Mixin"

    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit", string="Second unit"
    )
    secondary_uom_qty = fields.Float(
        string="Secondary Qty", digits="Product Unit of Measure"
    )


class StockMove(models.Model):
    _inherit = ["stock.move", "stock.secondary.unit.mixin"]
    _name = "stock.move"

    def _merge_moves_fields(self):
        res = super()._merge_moves_fields()
        res["secondary_uom_qty"] = self[-1:].secondary_uom_qty
        return res


class StockMoveLine(models.Model):
    _inherit = ["stock.move.line", "stock.secondary.unit.mixin"]
    _name = "stock.move.line"

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
