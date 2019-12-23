# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInventoryLine(models.Model):
    """Class to inherit model stock.inventory.line"""

    _inherit = "stock.inventory.line"

    reason = fields.Char(help="Type in a reason for the " "product quantity change")
    preset_reason_id = fields.Many2one("stock.inventory.line.reason")

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        """Function to super _get_move_value"""
        res = super(StockInventoryLine, self)._get_move_values(
            qty, location_id, location_dest_id, out
        )
        context = (
            self.reason if not self.preset_reason_id else self.preset_reason_id.name
        )
        if res.get("origin"):
            res["origin"] = " ,".join([res.get("origin"), context])
        else:
            res["origin"] = context
        if self.preset_reason_id:
            res["preset_reason_id"] = self.preset_reason_id.id
        return res
