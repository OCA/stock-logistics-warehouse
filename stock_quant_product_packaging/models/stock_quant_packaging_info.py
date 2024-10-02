# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuantPackagingInfo(models.Model):
    _name = "stock.quant.packaging.info"
    _description = "Additional information on the packaging repartition of the quant"

    quant_id = fields.Many2one(
        "stock.quant", index=True, required=True, ondelete="cascade"
    )
    packaging_id = fields.Many2one(
        "product.packaging", index=True, required=True, ondelete="cascade"
    )
    qty_per_pkg = fields.Float(
        string="Quantity per package",
        related="packaging_id.qty",
        digits="Product Unit of Measure",
    )
    qty = fields.Float(string="Quantity", digits="Product Unit of Measure")
