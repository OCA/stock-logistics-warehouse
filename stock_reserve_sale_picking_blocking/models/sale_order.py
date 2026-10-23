# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        return super(
            SaleOrder, self.with_context(keep_delivery_blocked_reservations=True)
        ).action_confirm()

    def action_cancel(self):
        orders = self
        if self._show_cancel_wizard():
            orders = self.with_context(keep_delivery_blocked_reservations=True)
        return super(SaleOrder, orders).action_cancel()

    def action_remove_delivery_block(self):
        self.filtered(lambda so: so.state == "sale").release_all_stock_reservation()
        return super().action_remove_delivery_block()

    def release_all_stock_reservation(self):
        orders = self
        if self.env.context.get("keep_delivery_blocked_reservations"):
            orders = self.filtered(lambda so: not so.delivery_block_id)
        return super(SaleOrder, orders).release_all_stock_reservation()
