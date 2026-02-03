# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_open_lot(self):
        self.ensure_one()
        if not self.lot_id:
            raise UserError(
                self.env._("No lot or serial number linked to this move line!")
            )
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.lot",
            "view_mode": "form",
            "res_id": self.lot_id.id,
            "target": "current",
        }
