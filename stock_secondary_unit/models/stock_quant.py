# Copyright 2025 Quartile (https://wwww.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = ["stock.quant", "product.secondary.unit.mixin"]
    _name = "stock.quant"
    _secondary_unit_fields = {"qty_field": "quantity", "uom_field": "product_uom_id"}

    secondary_uom_id = fields.Many2one(
        related="product_id.stock_secondary_uom_id",
        store=True,
        default=None,
    )
    # Need precompute=False since secondary_uom_id is not precompute field and we
    # shouldn't depend for compute method of precompute field.
    secondary_uom_qty = fields.Float(precompute=False)

    @api.model
    def _get_secondary_uom_qty_depends(self):
        return super()._get_secondary_uom_qty_depends() + ["secondary_uom_id"]
