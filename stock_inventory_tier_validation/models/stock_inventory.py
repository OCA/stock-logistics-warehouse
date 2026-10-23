# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _name = "stock.inventory"
    _inherit = ["stock.inventory", "tier.validation"]
    _state_from = ["in_progress"]
    _state_to = ["done"]

    _tier_validation_manual_config = False

    @api.model
    def _is_tier_validation_required(self, company):
        return bool(
            self.env["tier.definition"].search_count(
                [("model", "=", self._name), ("company_id", "in", [False, company.id])],
                limit=1,
            )
        )

    def action_state_to_done(self):
        self.ensure_one()
        if not self._is_tier_validation_required(self.company_id):
            return super().action_state_to_done()
        quants = self.stock_quant_ids.filtered(
            lambda q: q.current_inventory_id == self and q.inventory_quantity_set
        )
        outdated = quants.filtered("is_outdated")
        if outdated:
            raise UserError(
                _(
                    "The stock of the following products has changed since they "
                    "were counted. Restart the validation and count them again:"
                    "\n%(products)s",
                    products="\n".join(outdated.product_id.mapped("display_name")),
                )
            )
        if self.state != "done":
            self.write({"state": "done"})
        if quants:
            quants.with_context(inventory_name=self.name)._apply_inventory()
            quants.inventory_quantity_set = False
        # super() writes the state again, which would fail with tier validation
        # exceptions as the adjustment is already validated
        return super(
            StockInventory, self.with_context(skip_validation_check=True)
        ).action_state_to_done()
