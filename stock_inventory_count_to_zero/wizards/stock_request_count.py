# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRequestCount(models.TransientModel):
    _inherit = "stock.request.count"
    set_count = fields.Selection(
        selection_add=[("zero", "Set to zero")], ondelete={"zero": "cascade"}
    )

    def action_request_count(self):
        if self.set_count == "zero":
            self.quant_ids.filtered(
                lambda q: not q.inventory_quantity_set
            ).action_set_inventory_quantity_recount_to_zero()
            self.quant_ids.with_context(inventory_mode=True).write(
                self._get_values_to_write()
            )
        else:
            return super(StockRequestCount, self).action_request_count()
