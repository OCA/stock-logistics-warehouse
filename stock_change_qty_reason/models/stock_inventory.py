# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    reason = fields.Char(help="Type in a reason for the " "product quantity change")
    preset_reason_id = fields.Many2one("stock.inventory.line.reason")

    def _get_inventory_lines_values(self):
        vals = super(StockInventory, self)._get_inventory_lines_values()
        for val in vals:
            if self.preset_reason_id:
                val["preset_reason_id"] = self.preset_reason_id.id
            elif self.reason:
                val["reason"] = self.reason
        return vals

    @api.onchange("reason")
    def onchange_reason(self):
        for line in self.line_ids:
            line.reason = self.reason

    @api.onchange("preset_reason_id")
    def onchange_preset_reason(self):
        for line in self.line_ids:
            line.preset_reason_id = self.preset_reason_id
