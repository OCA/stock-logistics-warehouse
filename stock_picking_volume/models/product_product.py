# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_volume_for_qty(self, qty, from_uom=None):
        """Return the volume for the given qty.

        This method is meant to be inherited to change the volume
        computation for a specific product.

        qty: float quantity to compute the volume for.
        from_uom: uom of given qty

        An override of this method could take into account the packaging
        of the product to compute the volume. (using the volume information
        on the packaging provided by the module stock_quant_package_dimension
        and the method product_qty_by_packaging on the product provided by the
        module stock_packaging_calculator)
        """
        if not self:
            return 0.0
        self.ensure_one()
        qty = from_uom and from_uom._compute_quantity(qty, self.uom_id) or qty
        return qty * self.volume
