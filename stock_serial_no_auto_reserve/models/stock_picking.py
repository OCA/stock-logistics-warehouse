# Copyright 2024 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_available = fields.Boolean(
        "Is Available", compute="_compute_is_available", store=True
    )

    @api.depends("state")
    def _compute_is_available(self):
        self.is_available = False
        for picking in self.filtered(lambda p: p.state == "waiting"):
            unassigned_moves = picking.move_ids_without_package.filtered(
                lambda a: a.state == "waiting"
            )  # this filters out the 'assigned' ones, for which items are already reserved
            if this.move_ids_without_package:
                this.is_available = all(
                    [
                        m.forecast_availability == m.product_uom_qty
                        and m.reserved_availability
                        < m.product_uom_qty  # Not sure if this line is necessary
                        and not m.forecast_expected_date
                        for m in this.move_ids_without_package
                    ]
                )
