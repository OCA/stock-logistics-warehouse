# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    manual_cost = fields.Monetary(
        compute="_compute_manual_cost",
        store=True,
        readonly=False,
    )

    @api.depends("inventory_diff_quantity", "product_id.standard_price")
    def _compute_manual_cost(self):
        for record in self:
            record.manual_cost = record.product_id.standard_price

    @api.model
    def _get_inventory_fields_write(self):
        """Returns a list of fields user can edit when editing a quant in `inventory_mode`."""
        res = super()._get_inventory_fields_write()
        res += ["manual_cost"]
        return res

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out
        )
        res["manual_cost"] = self.manual_cost
        return res
