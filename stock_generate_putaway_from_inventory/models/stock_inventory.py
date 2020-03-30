# © 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def action_generate_putaway_strategy(self):
        for inventory in self:
            inventory._generate_putaway_strategy()

    def _get_putaway_strategy(self, loc):
        if loc.putaway_strategy_id:
            return loc.putaway_strategy_id
        elif loc.location_id:
            return self._get_putaway_strategy(loc.location_id)

    def _update_product_putaway_strategy(self, inventory_line, strategy):
        putaway_line_obj = self.env["stock.fixed.putaway.strat"]
        putaway_line = putaway_line_obj.search(
            [
                ("product_id", "=", inventory_line.product_id.id),
                ("putaway_id", "=", strategy.id),
            ]
        )
        if putaway_line:
            putaway_line.write(
                {"fixed_location_id": inventory_line.location_id.id}
            )
        else:
            putaway_line_obj.create(
                {
                    "product_id": inventory_line.product_id.id,
                    "fixed_location_id": inventory_line.location_id.id,
                    "putaway_id": strategy.id,
                }
            )

    def _generate_putaway_strategy(self):
        if self.state != "done":
            raise ValidationError(
                _(
                    "Please validate the inventory before generating "
                    "the putaway strategy."
                )
            )
        putaway = self._get_putaway_strategy(self.location_id)
        if not putaway:
            raise ValidationError(
                _(
                    "Inventory location doesn't have a putaway strategy. "
                    "Please set a putaway strategy on the inventory's "
                    "location."
                )
            )
        for line in self.line_ids:
            if line.product_qty > 0:
                self._update_product_putaway_strategy(line, putaway)
