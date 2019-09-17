# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    virtual_reserved_qty = fields.Float(
        "Virtual Reserved Quantity",
        compute="_compute_virtual_reserved_qty",
        help="Quantity to be reserved by older operations that do not have"
        " a real reservation yet",
    )

    # TODO does it make sense to have the 'virtual reserved qty' on product
    # alongside other quantities?
    @api.depends()
    def _compute_virtual_reserved_qty(self):
        for move in self:
            move.virtual_reserved_qty = move._get_virtual_reserved_qty()

    def _should_compute_virtual_reservation(self):
        return (
            self.picking_code == "outgoing"
            and not self.product_id.type == "consu"
            and not self.location_id.should_bypass_reservation()
        )

    def _get_virtual_reserved_qty(self):
        if not self._should_compute_virtual_reservation():
            return 0.
        # TODO verify where we should check the quantity for (full
        # warehouse?)
        available = self.product_id.qty_available
        return max(
            min(available - self._virtual_reserved_qty(), self.product_qty), 0.
        )

    def _virtual_quantity_domain(self):
        states = ("draft", "confirmed", "partially_available", "waiting")
        domain = [
            ("state", "in", states),
            ("product_id", "=", self.product_id.id),
            # FIXME might need to write an optimized SQL here, this one
            # will be slow with the DB growing as picking_code is a
            # related to picking_id.picking_type_id.code ->
            # generates a query searching all outgoing stock.picking first
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

    # TODO As we will defer the creation of the previous operations before
    # doing this reservation, we might not even need to do this, since
    # the previous operation will reserve only what's possible. Still,
    # for the one-step...
    # def _update_reserved_quantity(
    #     self,
    #     need,
    #     available_quantity,
    #     location_id,
    #     lot_id=None,
    #     package_id=None,
    #     owner_id=None,
    #     strict=True,
    # ):
    #     # TODO how to ensure this is done before any other override of the
    #     # method...
    #     if self._should_compute_virtual_reservation():
    #         virtual_reserved = self._virtual_reserved_qty()
    #         available_quantity = max(available_quantity - virtual_reserved, 0.)
    #     return super()._update_reserved_quantity(
    #         need,
    #         available_quantity,
    #         location_id,
    #         lot_id=lot_id,
    #         package_id=package_id,
    #         owner_id=owner_id,
    #         strict=strict,
    #     )

    def _action_assign(self):
        self._run_stock_rule()
        return super()._action_assign()

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
            available_quantity = move._get_virtual_reserved_qty()
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
