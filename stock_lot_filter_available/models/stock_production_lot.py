# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import operator as operator_lib

from odoo import _, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    product_qty = fields.Float(search="_search_product_qty")

    def _search_product_qty(self, operator, value):
        operator_mapping = {
            ">": operator_lib.gt,
            ">=": operator_lib.ge,
            "<": operator_lib.lt,
            "<=": operator_lib.le,
            "=": operator_lib.eq,
            "!=": operator_lib.ne,
        }
        if operator not in operator_mapping:
            raise ValueError(_("Unsupported search"))
        ids = []
        domain = [
            ("location_id.usage", "in", ["internal", "transit"]),
            ("lot_id", "!=", False),
        ]
        groups = self.env["stock.quant"].read_group(
            domain, ["lot_id", "quantity"], ["lot_id"]
        )
        involved_lot_ids = [group["lot_id"][0] for group in groups]
        if (
            (operator == "=" and value == 0)
            or (operator == "<" and value > 0)
            or (operator == "<=" and value >= 0)
        ):
            ids.extend(
                self.env["stock.production.lot"]
                .search([("id", "not in", involved_lot_ids)])
                .ids
            )
        for group in groups:
            if operator_mapping[operator](group["quantity"], value):
                ids.append(group["lot_id"][0])
        return [("id", "in", ids)]
