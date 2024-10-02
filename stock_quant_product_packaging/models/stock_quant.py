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

    @api.depends("packaging_info_ids.qty", "packaging_info_ids.qty_per_pkg")
    def _compute_packaging_info_str(self):
        for rec in self:
            # res = ""
            # print("rec.packaging_info_ids")
            # print(rec.packaging_info_ids)
            # for info in rec.packaging_info_ids:
            #     if info.qty:
            #         print("res+=")
            #         print(info.qty_per_pkg)
            #         print(info.qty)
            #         res += f"A {info.qty_per_pkg}: {info.qty}, "
            # res = res[:-2] if res else ""
            # rec.packaging_info_str = res
            res = ", ".join(
                [f"{info.qty_per_pkg}: {info.qty}" for info in rec.packaging_info_ids]
            )
            if res:
                res = res[:-2]
            rec.packaging_info_str = res
