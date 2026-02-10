# Copyright 2026 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockInventoryAdjustmentName(models.TransientModel):
    _inherit = "stock.inventory.adjustment.name"

    inventory_location_id = fields.Many2one(
        "stock.location",
        domain="[('usage', '=', 'inventory')]",
        help="Counterpart location for the inventory adjustment. "
        "If empty, the default from the product category is used.",
    )

    def action_apply(self):
        if self.inventory_location_id:
            self = self.with_context(
                inventory_location_id=self.inventory_location_id.id,
            )
        return super().action_apply()
