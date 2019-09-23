# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api,  models
from odoo.osv import expression
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_compute_virtual_reservation(self):
        return (
            self.picking_code == "outgoing"
            and not self.product_id.type == "consu"
            and not self.location_id.should_bypass_reservation()
        )

    def _virtual_available_qty(self):
        if not self._should_compute_virtual_reservation():
            return 0.
        # TODO available must be the qty in the warehouse Stock location
        available = self.product_id.qty_available
        return max(
            min(available - self._virtual_reserved_qty(), self.product_qty), 0.
        )

    def _virtual_quantity_domain(self):
        # FIXME partially_available shouldn't exist if we split them?
        # would make the qty wrong anyway
        states = ("draft", "confirmed", "partially_available", "waiting")
        domain = [
            ("state", "in", states),
            ("product_id", "=", self.product_id.id),
            ("picking_code", "=", "outgoing"),
            # TODO easier way to customize date field to use
            ("date", "<=", self.date),
        ]
        # TODO priority?
        return domain

    def _virtual_reserved_qty(self):
        previous_moves = self.search(
            expression.AND(
                [self._virtual_quantity_domain(), [("id", "!=", self.id)]]
            )
        )
        virtual_reserved = sum(
            previous_moves.mapped(
                lambda move: max(
                    move.product_qty - move.reserved_availability, 0.
                )
            )
        )
        return virtual_reserved

    # TODO add a public method + wizard on moves
    # def _action_assign(self):
    #     self._run_stock_rule()
    #     return super()._action_assign()

    @api.multi
    def _run_stock_rule(self):
        """Launch procurement group run method with remaining quantity

        As we only generate chained moves for the quantity available minus the
        virtually reserved quantity, to delay the reservation at the latest, we
        have to periodically retry to assign the remaining quantities.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            if move.rule_id.action != "pull":
                continue
            if move.state not in (
                "waiting",
                "confirmed",
                "partially_available",
            ):
                continue
            if move.product_id.type not in ("consu", "product"):
                continue
            # do not use the computed field, because it will keep
            # a value in cache that we cannot invalidate declaratively
            available_quantity = move._virtual_available_qty()
            if (
                float_compare(
                    available_quantity, 0, precision_digits=precision
                )
                <= 0
            ):
                continue

            # TODO probably not the good way to do this?
            already_in_pull = sum(move.mapped("move_orig_ids.product_qty"))
            remaining = move.product_uom_qty - already_in_pull

            if float_compare(remaining, 0, precision_digits=precision) <= 0:
                continue

            # TODO split the 'out' picking before calling the pull rull
            quantity = min(remaining, available_quantity)
            values = move._prepare_procurement_values()

            self.env["procurement.group"].with_context(
                _rule_no_virtual_defer=True
            ).run_defer(
                move.product_id,
                quantity,
                move.product_uom,
                move.location_id,
                move.origin,
                values,
            )
        return True
