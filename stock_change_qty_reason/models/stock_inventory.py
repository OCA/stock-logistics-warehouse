# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    reason = fields.Char(
        help="Type in a reason for the " "product quantity change",
        states={"done": [("readonly", True)]},
    )
    preset_reason_id = fields.Many2one(
        "stock.inventory.reason", states={"done": [("readonly", True)]}
    )

    def _get_quants(self, locations):
        stock_quant_ids = super()._get_quants(locations)
        if self.preset_reason_id:
            stock_quant_ids.write({"preset_reason_id": self.preset_reason_id.id})
        elif self.reason:
            stock_quant_ids.write({"reason": self.reason})
        return stock_quant_ids
