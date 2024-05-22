# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    stock_quant_packaging_infos = fields.Char(
        "Stock pkg. info",
        compute="_compute_stock_quant_packaging_infos",
        help="Quantities by packagings in format qty per package: qty",
    )

    def _compute_stock_quant_packaging_infos(self):
        for rec in self:
            rec.stock_quant_packaging_infos = ", ".join(
                rec.stock_quant_ids.mapped("packaging_info_str")
            )
