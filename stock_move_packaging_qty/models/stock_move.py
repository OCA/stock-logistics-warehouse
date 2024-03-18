# Copyright 2020 Camptocamp SA
# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.move"

    product_packaging_qty = fields.Float(
        string="Pkg. Qty.",
        compute="_compute_product_packaging_qty",
        inverse="_inverse_product_packaging_qty",
        help="Amount of packages demanded.",
    )

    @api.depends(
        "product_qty", "product_uom", "product_packaging_id", "product_packaging_id.qty"
    )
    def _compute_product_packaging_qty(self):
        for move in self:
            if (
                not move.product_packaging_id
                or move.product_qty == 0
                or move.product_packaging_id.qty == 0
            ):
                move.product_packaging_qty = 0
                continue
            # Consider uom
            move.product_packaging_qty = (
                move.product_uom_qty / move._get_single_package_uom_qty()
            )

    @api.onchange("product_packaging_qty")
    def _inverse_product_packaging_qty(self):
        """Store the quantity in the product's UoM.

        This inverse is also an onchange because otherwise changes are not
        reflected live.
        """
        for move in self:
            if move.product_packaging_id and move.product_packaging_qty:
                uom_factor = move._get_single_package_uom_qty()
                move.product_uom_qty = move.product_packaging_qty * uom_factor

    @api.onchange("product_packaging_id")
    def _onchange_product_packaging(self):
        """Add a default qty if the packaging has an invalid value."""
        if not self.product_packaging_id:
            self.product_packaging_qty = 0
            return
        self.product_uom_qty = (
            self.product_packaging_id._check_qty(self.product_uom_qty, self.product_uom)
            or self._get_single_package_uom_qty()
        )

    def _get_single_package_uom_qty(self):
        """Return the quantity of a single package in the move's UoM."""
        self.ensure_one()
        if not self.product_packaging_id:
            return 0
        return self.product_packaging_id.product_uom_id._compute_quantity(
            self.product_packaging_id.qty, self.product_uom
        )
