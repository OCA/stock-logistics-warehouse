# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMoveRelease(models.TransientModel):
    _name = "stock.move.release"
    _description = "Stock Move Release"

    def release(self):
        moves = (
            self.env["stock.move"]
            .browse(self.env.context.get("active_ids", []))
            .exists()
        )
        moves.release_available_to_promise()
        return {"type": "ir.actions.act_window_close"}
