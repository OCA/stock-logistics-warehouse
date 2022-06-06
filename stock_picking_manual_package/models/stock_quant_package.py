# Copyright 2022 Sergio Teruel - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    @api.model_create_multi
    def create(self, vals_list):
        package = self.env.context.get("put_in_pack_package_id", False)
        if not package:
            return super().create(vals_list)
        return package
