# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, exceptions, models
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _reserve_quant(self, quantity, available_quantity):
        """Reserve a quantity on a quant.

        Return the adjusted quantity, the still available quantity after
        the reservation occurred and the reserved quantity for this quant.

        Extracted from StockQuant._update_reserved_quantity().

        :param quantity: the total quantity required for a move, maybe not
        entirely reserved by the current quant
        :param available_quantity: total available quantity for the product
        (across all quants)
        """
        rounding = self.product_id.uom_id.rounding
        reserved = 0.
        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            max_quantity_on_quant = self.quantity - self.reserved_quantity
            max_compare_0 = float_compare(
                max_quantity_on_quant, 0, precision_rounding=rounding
            )
            if max_compare_0 <= 0:
                return quantity, available_quantity, 0
            max_quantity_on_quant = min(max_quantity_on_quant, quantity)
            self.reserved_quantity += max_quantity_on_quant
            reserved = max_quantity_on_quant
            quantity -= max_quantity_on_quant
            available_quantity -= max_quantity_on_quant
        else:
            max_quantity_on_quant = min(self.reserved_quantity, abs(quantity))
            self.reserved_quantity -= max_quantity_on_quant
            reserved = -max_quantity_on_quant
            quantity += max_quantity_on_quant
            available_quantity += max_quantity_on_quant
        return quantity, available_quantity, reserved

    @api.multi
    def _update_reserved_get_available(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        """Get available quants when updating reservation for product

        Extracted from StockQuant._update_reserved_quantity().
        """
        rounding = product_id.uom_id.rounding

        def is_greater(value, other):
            return float_compare(value, other, precision_rounding=rounding) > 0

        def is_lesser(value, other):
            return float_compare(value, other, precision_rounding=rounding) < 0

        if is_greater(quantity, 0):
            # if we want to reserve
            available_quantity = self._get_available_quantity(
                product_id,
                location_id,
                lot_id=lot_id,
                package_id=package_id,
                owner_id=owner_id,
                strict=strict,
            )
            if is_greater(quantity, available_quantity):
                raise exceptions.UserError(
                    _(
                        "It is not possible to reserve more products"
                        " of %s than you have in stock."
                    )
                    % product_id.display_name
                )
            return available_quantity
        elif is_lesser(quantity, 0):
            # if we want to unreserve
            available_quantity = sum(self.mapped("reserved_quantity"))
            if is_greater(abs(quantity), available_quantity):
                raise exceptions.UserError(
                    _(
                        "It is not possible to unreserve more"
                        " products of %s than you have in stock."
                    )
                    % product_id.display_name
                )
            return available_quantity
        else:
            return 0.

    @api.multi
    def _update_reserved_quantity_packaging(
        self,
        product_id,
        location_id,
        quantity,
        available_quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        """Try to reserve full packaging first

        When packaging is configured on products, this method will take
        priority over the removal strategy (fifo, lifo, ...). It will try
        to reserve full packaging first.

        Example:

        * Product X is configured with pallets of 100 units.
        * Location 1 has 80 units, Location 2 has 100 units.
        * Location 1 units were input before Location 2.

        Normally, the reservation would be:

        * 80 units from Location 1
        * 20 units from Location 2

        Normally, the (fifo) reservation would be:

        * 100 units from Location 2

        When the quantity is not a full packaging, there is no change:

        * Product X is configured with pallets of 100 units.
        * Location 1 has 80 units, Location 2 has 90 units.
        * Location 1 units were input before Location 2.

        We will have:

        * 80 units from Location 1
        * 10 units from Location 2

        """

        rounding = product_id.uom_id.rounding

        def is_greater_eq(value, other):
            return (
                float_compare(value, other, precision_rounding=rounding) >= 0
            )

        # we'll walk the packagings from largest to smallest to have the
        # largest containers as possible (1 pallet rather than 10 boxes)
        packaging_quantities = sorted(
            product_id.packaging_ids.mapped("qty"), reverse=True
        )
        reserved_quants = []
        for pack_quantity in packaging_quantities:
            while is_greater_eq(
                available_quantity, quantity
            ) and is_greater_eq(quantity, pack_quantity):
                # We have to keep the original sorting of the quants (fifo...),
                # unless we find a "matching" packaging, in which case we
                # ignore the order.
                for quant in self:
                    quant_remaining = quant.quantity - quant.reserved_quantity
                    if is_greater_eq(
                        quant_remaining, pack_quantity
                    ) and is_greater_eq(quantity, quant_remaining):
                        (
                            quantity,
                            available_quantity,
                            reserved,
                        ) = quant._reserve_quant(quantity, available_quantity)
                        if reserved:
                            reserved_quants.append((quant, reserved))
                            break
                else:
                    # We reach this else when the 'for' did not hit
                    # break. Meaning, no quant was found for this quantity.
                    # Break the 'while' loop so we continue with the next
                    # packaging quantity.
                    break
        return quantity, available_quantity, reserved_quants

    @api.model
    def _update_reserved_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        # In this override, we are going to try to reserve quants matching full
        # packagings first. To do so, we have to repeat things done in the
        # super method before calling super for the quantity we could not
        # assign based on packaging quantities. Concretely, the repeated
        # operations are:
        # * call to _gather to get quants
        # * get available quantity and check it's validity (extracted in
        #   _update_reserved_get_available, but the super method does it
        #   innerly.
        #
        # super() will be called with the remaining quantity (which can be 0)
        self = self.sudo()
        rounding = product_id.uom_id.rounding

        quants = self._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

        available_quantity = quants._update_reserved_get_available(
            product_id,
            location_id,
            quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
        if not available_quantity:
            return []

        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # Only on reservation, try to reserve full packaging
            (
                quantity,
                available_quantity,
                reserved_quants,
            ) = quants._update_reserved_quantity_packaging(
                product_id,
                location_id,
                quantity,
                available_quantity,
                lot_id=lot_id,
                package_id=package_id,
                owner_id=owner_id,
                strict=strict,
            )

        # Reserve the rest, which could not be reserved in full packaging
        return reserved_quants + super()._update_reserved_quantity(
            product_id,
            location_id,
            quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
