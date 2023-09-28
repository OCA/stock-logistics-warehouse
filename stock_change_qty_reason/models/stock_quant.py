# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    """Class to inherit model stock.quant"""

    _inherit = "stock.quant"

    reason = fields.Char(help="Type in a reason for the product quantity change")
    preset_reason_id = fields.Many2one("stock.quant.reason")

    @api.model
    def _get_inventory_fields_write(self):
        res = super()._get_inventory_fields_write()
        res.extend(["reason", "preset_reason_id"])
        return res

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        # Called when user manually set a new quantity (via `inventory_quantity`)
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out
        )
        # Aftect the reason to the move line
        context = (
            self.reason if not self.preset_reason_id else self.preset_reason_id.name
        )
        line = res["move_line_ids"][0][2]
        line["reason"] = context
        if res.get("origin"):
            res["origin"] = " ,".join([res.get("origin"), context])
        else:
            res["origin"] = context
        if self.preset_reason_id:
            line["preset_reason_id"] = self.preset_reason_id.id
            self.preset_reason_id = False
        if self.reason:
            self.reason = False
        return res
