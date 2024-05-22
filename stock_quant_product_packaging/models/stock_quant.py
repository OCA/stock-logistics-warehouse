# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    packaging_info_ids = fields.One2many(
        "stock.quant.packaging.info",
        "quant_id",
        string="Packaging additional information",
    )
    packaging_info_str = fields.Char(
        compute="_compute_packaging_info_str",
        string="Qty per pkg. qty",
        help="Quantities by packagings in format qty per package: qty",
        store=True,
    )

    @api.depends("packaging_info_ids")
    def _compute_packaging_info_str(self):
        for rec in self:
            rec.packaging_info_str = ", ".join(
                [f"{info.qty_per_pkg}: {info.qty}" for info in rec.packaging_info_ids]
            )
