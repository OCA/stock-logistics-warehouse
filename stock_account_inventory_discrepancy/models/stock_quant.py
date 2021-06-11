# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class Quant(models.Model):
    _inherit = "stock.quant"

    def _has_over_discrepancy(self, qty=None):
        self.ensure_one()
        whs = self.location_id.get_warehouse()
        if self.location_id.discrepancy_amount_threshold > 0.0:
            discrepancy_amount_threshold = self.location_id.discrepancy_amount_threshold
        elif whs.discrepancy_amount_threshold > 0.0:
            discrepancy_amount_threshold = whs.discrepancy_amount_threshold
        else:
            return False

        discrepancy_qty = qty or self.quantity
        cost = self.product_id.standard_price
        discrepancy_amount = discrepancy_qty * cost

        return abs(discrepancy_amount) > discrepancy_amount_threshold > 0

    def _set_inventory_quantity(self):
        for rec in self:
            variance = self.inventory_quantity - rec.quantity
            if rec._has_over_discrepancy(qty=variance) and not self.user_has_groups(
                "stock_inventory_discrepancy.group_stock_inventory_validation_always"
            ):
                raise UserError(
                    _(
                        "The Qty Update is over the Discrepancy Threshold.\n "
                        "Please, contact a user with rights to perform "
                        "this action."
                    )
                )
        return super(Quant, self)._set_inventory_quantity()
