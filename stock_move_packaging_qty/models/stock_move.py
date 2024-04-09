# Copyright 2020 Camptocamp SA
# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import _, api, exceptions, fields, models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    product_packaging_qty = fields.Float(
        string="Pkgs. Demand",
        compute="_compute_product_packaging_qty",
        inverse="_inverse_product_packaging_qty",
        help="Amount of product packagings demanded.",
    )
    product_packaging_qty_done = fields.Float(
        string="Pkgs. Done",
        compute="_compute_product_packaging_qty_done",
        inverse="_inverse_product_packaging_qty_done",
        help="Amount of product packagings done.",
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

    @api.depends(
        "move_line_ids.product_packaging_qty_done",
        "move_line_nosuggest_ids.product_packaging_qty_done",
    )
    def _compute_product_packaging_qty_done(self):
        """Get the sum of done packaging qtys from move lines."""
        for move in self:
            lines = move._get_move_lines()
            move.product_packaging_qty_done = sum(
                lines.mapped("product_packaging_qty_done")
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

    def _inverse_product_packaging_qty_done(self):
        """Store the done packaging dqty in the move line if there's just one."""
        for move in self:
            lines = move._get_move_lines()
            # Setting 0 done pkgs with no lines? Nothing to do
            if not lines and not move.product_packaging_qty_done:
                continue
            if len(lines) != 1:
                raise exceptions.UserError(
                    _(
                        "There are %d move lines involved. "
                        "Please set their product packaging done qty directly.",
                        len(lines),
                    )
                )
            lines.product_packaging_qty_done = move.product_packaging_qty_done

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

    def _set_quantities_to_reservation(self):
        """Add packaging qtys when clicking on "Set Quantities"."""
        result = super()._set_quantities_to_reservation()
        digits = self.env["stock.move.line"].fields_get(["qty_done"], ["digits"])[
            "qty_done"
        ]["digits"][1]
        for line in self.move_line_ids:
            if float_compare(line.qty_done, line.reserved_uom_qty, digits):
                continue
            if not line.product_packaging_id:
                line.product_packaging_qty_done = 0
                continue
            line.product_packaging_qty_done = (
                line.product_packaging_id._check_qty(
                    line.qty_done, line.product_uom_id, "DOWN"
                )
                / line.product_packaging_id.qty
            )
        return result

    def _clear_quantities_to_zero(self):
        """Clear packaging qtys when clicking on "Clear Quantities"."""
        result = super()._clear_quantities_to_zero()
        for line in self.move_line_ids:
            if line.qty_done:
                continue
            line.product_packaging_qty_done = 0
        return result
