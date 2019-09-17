# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression


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
            if not move._should_compute_virtual_reservation():
                move.virtual_reserved_qty = 0.
                continue
            # TODO verify where we should check the quantity for (full
            # warehouse?)
            available = move.product_id.qty_available
            move.virtual_reserved_qty = max(
                min(
                    available - move._virtual_reserved_qty(), self.product_qty
                ),
                0.,
            )

    def _should_compute_virtual_reservation(self):
        return (
            self.picking_code == 'outgoing'
            and not self.product_id.type == "consu"
            and not self.location_id.should_bypass_reservation()
        )

    def _virtual_quantity_domain(self, location_id=None):
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

    def _virtual_reserved_qty(self, location_id=None):
        previous_moves = self.search(
            expression.AND(
                [
                    self._virtual_quantity_domain(location_id=location_id),
                    [("id", "!=", self.id)],
                ]
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
    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        # TODO how to ensure this is done before any other override of the
        # method...
        if self._should_compute_virtual_reservation():
            virtual_reserved = self._virtual_reserved_qty(
                location_id=location_id
            )
            available_quantity = max(available_quantity - virtual_reserved, 0.)

        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
