# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    product_qty = fields.Float(search="_search_product_qty")

    @api.model
    def _is_unsupported_search_operator(self, operator):
        return operator != ">"

    def _search_product_qty(self, operator, value):
        if self._is_unsupported_search_operator(operator) or value:
            raise ValueError(_("Unsupported search"))
        ids = []
        domain = [
            ("location_id.usage", "in", ["internal", "transit"]),
            ("lot_id", "!=", False),
        ]
        groups = self.env["stock.quant"].read_group(
            domain, ["lot_id", "quantity"], ["lot_id"]
        )
        for group in groups:
            if group["quantity"] > value:
                ids.append(group["lot_id"][0])
        return [("id", "in", ids)]
