# Copyright 2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# Copyright 2020 Camptocamp

import logging

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

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
        try:
            return super()._update_reserved_quantity(
                product_id,
                location_id,
                quantity,
                lot_id=lot_id,
                package_id=package_id,
                owner_id=owner_id,
                strict=strict,
            )
        except UserError as e:
            if (
                e.name
                == _(
                    "It is not possible to unreserve more products of %s "
                    "than you have in stock."
                )
                % product_id.display_name
            ):
                _logger.warning(
                    "You have unreserved more products of %s than you have "
                    "in stock in location %s. "
                    % (product_id.display_name, location_id.display_name)
                )
                # if we are here means that the quantity is greater than
                # available_qty, so in order to unreserve without getting an
                # error we need to decrease the quantity to unreserve to
                # match the quantity actually reserved on the quant.
                # we are assuming there is only one quant by location/product
                rounding = product_id.uom_id.rounding
                quants = self._gather(
                    product_id,
                    location_id,
                    lot_id=lot_id,
                    package_id=package_id,
                    owner_id=owner_id,
                    strict=strict,
                )
                available_quantity = sum(quants.mapped("quantity"))
                available_reserved_quantity = sum(quants.mapped("reserved_quantity"))
                # the current qty is less than what we want to unreserve:
                # update it
                if (
                    float_compare(
                        available_quantity,
                        -quantity,
                        precision_rounding=rounding,
                    )
                    < 0
                ):
                    self._update_available_quantity(
                        product_id,
                        location_id,
                        -quantity - available_quantity,
                        lot_id=lot_id,
                        package_id=package_id,
                        owner_id=owner_id,
                    )
                # only unreserve what we have reserved, this a pathologic
                # case...
                return super()._update_reserved_quantity(
                    product_id,
                    location_id,
                    -available_reserved_quantity,
                    lot_id=lot_id,
                    package_id=package_id,
                    owner_id=owner_id,
                    strict=strict,
                )
            else:
                raise
