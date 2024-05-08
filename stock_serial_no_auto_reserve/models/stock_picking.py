# Copyright 2024 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_available = fields.Boolean(
        "Is available but not ready", compute="_compute_is_available", store=True
    )

    @api.depends("state", "move_ids_without_package.is_available")
    def _compute_is_available(self):
        for picking in self:
            picking.is_available = picking.state in ("waiting", "confirmed") and all(
                [
                    m.state in ("assigned", "done") or m.is_available
                    for m in picking.move_ids_without_package
                ]
            )
