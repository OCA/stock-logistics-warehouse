# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    date_priority = fields.Datetime(
        string="Priority Date",
        index=True,
        default=fields.Datetime.now,
        help="Date/time used to sort moves to deliver first. "
        "Used to calculate the virtual quantity.",
    )
    virtual_available_qty = fields.Float(
        "Virtual Available Quantity",
        compute="_compute_virtual_available_qty",
        help="Available quantity minus virtually reserved by older"
        " operations that do not have a real reservation yet",
    )

    @api.depends()
    def _compute_virtual_available_qty(self):
        for move in self:
            move.virtual_available_qty = move._virtual_available_qty()

    def _should_compute_virtual_reservation(self):
        return (
            self.picking_code == "outgoing"
            and not self.product_id.type == "consu"
            and not self.location_id.should_bypass_reservation()
        )

    def _virtual_available_qty(self):
        if not self._should_compute_virtual_reservation():
            return 0.
        available = self.product_id.with_context(
            location=self.warehouse_id.lot_stock_id.id
        ).qty_available
        return max(
            min(available - self._virtual_reserved_qty(), self.product_qty), 0.
        )

    def _virtual_quantity_domain(self):
        domain = [
            ("state", "in", ("confirmed", "waiting")),
            ("product_id", "=", self.product_id.id),
            ("picking_code", "=", "outgoing"),
            ("date_priority", "<=", self.date_priority),
            ("warehouse_id", "=", self.warehouse_id.id),
        ]
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

    @api.multi
    def release_virtual_reservation(self):
        self._run_stock_rule()

    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)
        # The method set procure_method as 'make_to_stock' by default on split,
        # but we want to keep 'make_to_order' for chained moves when we split
        # a partially available move in _run_stock_rule().
        if self.env.context.get("procure_method"):
            vals["procure_method"] = self.env.context["procure_method"]
        return vals

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
            # FIXME what to do if there is no pull rule?
            # should we have a different state for moves that need a release?
            if move.state not in ("confirmed", "waiting"):
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

            quantity = min(move.product_uom_qty, available_quantity)
            remaining = move.product_uom_qty - quantity

            if float_compare(remaining, 0, precision_digits=precision) > 0:
                if move.picking_id.move_type == "one":
                    # we don't want to delivery unless we can deliver all at
                    # once
                    continue
                move.with_context(procure_method=move.procure_method)._split(
                    remaining
                )

            values = move._prepare_procurement_values()

            self.env["procurement.group"].run_defer(
                move.product_id,
                quantity,
                move.product_uom,
                move.location_id,
                move.origin,
                values,
            )

            pull_move = move
            while pull_move:
                if pull_move.state == "confirmed":
                    pull_move._action_assign()
                pull_move = pull_move.move_orig_ids

        return True
