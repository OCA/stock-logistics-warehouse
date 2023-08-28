# Copyright 2020 Camptocamp SA
# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.move"

    product_packaging_qty = fields.Float(
        string="Package quantity",
        compute="_compute_product_packaging_qty",
        inverse="_inverse_product_packaging_qty",
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
            if move.product_id.uom_id != move.product_uom:
                product_qty = move.product_uom._compute_quantity(
                    move.product_uom_qty, move.product_id.uom_id
                )
            else:
                product_qty = move.product_uom_qty
            move.product_packaging_qty = product_qty / move.product_packaging_id.qty

    def _prepare_product_packaging_qty_values(self):
        return {
            "product_uom_qty": self.product_packaging_id.qty
            * self.product_packaging_qty,
            "product_uom": self.product_packaging_id.product_uom_id.id,
        }

    def _inverse_product_packaging_qty(self):
        for move in self:
            if move.product_packaging_qty and not move.product_packaging_id:
                raise UserError(
                    _(
                        "You must define a package before setting a quantity "
                        "of said package."
                    )
                )
            if move.product_packaging_id and move.product_packaging_id.qty == 0:
                raise UserError(
                    _("Please select a packaging with a quantity bigger than 0")
                )
            if move.product_packaging_id and move.product_packaging_qty:
                move.write(move._prepare_product_packaging_qty_values())

    @api.onchange("product_packaging_id")
    def _onchange_product_packaging(self):
        if self.product_packaging_id:
            self.update(
                {
                    "product_packaging_qty": 1,
                    "product_uom_qty": self.product_packaging_id.qty,
                    "product_uom": self.product_id.uom_id,
                }
            )
        else:
            self.update({"product_packaging_qty": 0})
        if self.product_packaging_id:
            return self._check_package()

    @api.onchange("product_packaging_qty")
    def _onchange_product_packaging_qty(self):
        if self.product_packaging_qty and self.product_packaging_id:
            self.update(self._prepare_product_packaging_qty_values())

    @api.onchange("product_uom_qty", "product_uom")
    def _onchange_product_uom_check_package(self):
        return self._check_package()

    def _check_package(self):
        default_uom = self.product_id.uom_id
        pack = self.product_packaging_id
        qty = self.product_qty
        q = default_uom._compute_quantity(pack.qty, self.product_uom)
        if qty and q and round(qty % q, 2):
            newqty = qty - (qty % q) + q
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "This product is packaged by %(old_qty).2f %(old_uom)s. "
                        "You should use %(new_qty).2f %(new_uom)s."
                    )
                    % {
                        "old_qty": pack.qty,
                        "old_uom": default_uom.name,
                        "new_qty": newqty,
                        "new_uom": self.product_uom.name,
                    },
                },
            }
        return {}
