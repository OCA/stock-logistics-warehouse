# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.osv import expression
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    date_priority = fields.Datetime(
        string="Priority Date",
        index=True,
        default=fields.Datetime.now,
        help="Date/time used to sort moves to deliver first. "
        "Used to calculate the ordered available to promise.",
    )
    ordered_available_to_promise = fields.Float(
        "Ordered Available to Promise",
        compute="_compute_ordered_available_to_promise",
        digits=dp.get_precision("Product Unit of Measure"),
        help="Available to Promise quantity minus quantities promised "
        " to older promised operations.",
    )
    need_release = fields.Boolean()

    @api.depends()
    def _compute_ordered_available_to_promise(self):
        for move in self:
            move.ordered_available_to_promise = (
                move._ordered_available_to_promise()
            )

    def _should_compute_ordered_available_to_promise(self):
        return (
            self.picking_code == "outgoing"
            and not self.product_id.type == "consu"
            and not self.location_id.should_bypass_reservation()
        )

    def _ordered_available_to_promise(self):
        if not self._should_compute_ordered_available_to_promise():
            return 0.
        available = self.product_id.with_context(
            location=self.warehouse_id.lot_stock_id.id
        ).virtual_available
        return max(
            min(available - self._previous_promised_qty(), self.product_qty),
            0.,
        )

    def _previous_promised_quantity_domain(self):
        domain = [
            ("need_release", "=", True),
            ("product_id", "=", self.product_id.id),
            ("date_priority", "<=", self.date_priority),
            ("warehouse_id", "=", self.warehouse_id.id),
        ]
        return domain

    def _previous_promised_qty(self):
        previous_moves = self.search(
            expression.AND(
                [
                    self._previous_promised_quantity_domain(),
                    [("id", "!=", self.id)],
                ]
            )
        )
        promised_qty = sum(
            previous_moves.mapped(
                lambda move: max(
                    move.product_qty - move.reserved_availability, 0.
                )
            )
        )
        return promised_qty

    @api.multi
    def release_available_to_promise(self):
        self._run_stock_rule()

    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)
        # The method set procure_method as 'make_to_stock' by default on split,
        # but we want to keep 'make_to_order' for chained moves when we split
        # a partially available move in _run_stock_rule().
        if self.env.context.get("release_available_to_promise"):
            vals.update(
                {"procure_method": self.procure_method, "need_release": True}
            )
        return vals

    @api.multi
    def _run_stock_rule(self):
        """Launch procurement group run method with remaining quantity

        As we only generate chained moves for the quantity available minus the
        quantity promised to older moves, to delay the reservation at the
        latest, we have to periodically retry to assign the remaining
        quantities.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            if not move.need_release:
                continue
            if move.state not in ("confirmed", "waiting"):
                continue
            # do not use the computed field, because it will keep
            # a value in cache that we cannot invalidate declaratively
            available_quantity = move._ordered_available_to_promise()
            if (
                float_compare(
                    available_quantity, 0, precision_digits=precision
                )
                <= 0
            ):
                continue

            quantity = min(move.product_qty, available_quantity)
            remaining = move.product_qty - quantity

            if float_compare(remaining, 0, precision_digits=precision) > 0:
                if move.picking_id.move_type == "one":
                    # we don't want to delivery unless we can deliver all at
                    # once
                    continue
                move.with_context(release_available_to_promise=True)._split(
                    remaining
                )

            values = move._prepare_procurement_values()

            self.env["procurement.group"].run_defer(
                move.product_id,
                move.product_id.uom_id._compute_quantity(
                    quantity, move.product_uom, rounding_method="HALF-UP"
                ),
                move.product_uom,
                move.location_id,
                move.origin,
                values,
            )

            pull_move = move
            while pull_move:
                pull_move._action_assign()
                pull_move = pull_move.move_orig_ids

        return True
