# Copyright 2020 Camptocamp SA
# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class StockPicking(models.Model):
    _inherit = "stock.move"

    product_packaging = fields.Many2one(
        comodel_name="product.packaging",
        string="Package",
        default=False,
        check_company=True,
    )
    product_packaging_qty = fields.Float(
        string="Package quantity",
        compute="_compute_product_packaging_qty",
        inverse="_inverse_product_packaging_qty",
        digits=dp.get_precision("Product Unit of Measure"),
    )

    @api.depends(
        "product_qty", "product_uom", "product_packaging", "product_packaging.qty"
    )
    def _compute_product_packaging_qty(self):
        for move in self:
            if (
                not move.product_packaging
                or move.product_qty == 0
                or move.product_packaging.qty == 0
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
            move.product_packaging_qty = product_qty / move.product_packaging.qty

    def _prepare_product_packaging_qty_values(self):
        return {
            "product_uom_qty": self.product_packaging.qty * self.product_packaging_qty,
            "product_uom": self.product_packaging.product_uom_id.id,
        }

    def _inverse_product_packaging_qty(self):
        for move in self:
            if move.product_packaging_qty and not move.product_packaging:
                raise UserError(
                    _(
                        "You must define a package before setting a quantity "
                        "of said package."
                    )
                )
            if move.product_packaging and move.product_packaging.qty == 0:
                raise UserError(
                    _("Please select a packaging with a quantity bigger than 0")
                )
            if move.product_packaging and move.product_packaging_qty:
                move.write(move._prepare_product_packaging_qty_values())

    @api.onchange("product_packaging")
    def _onchange_product_packaging(self):
        if self.product_packaging:
            self.update(
                {
                    "product_packaging_qty": 1,
                    "product_uom_qty": self.product_packaging.qty,
                    "product_uom": self.product_id.uom_id,
                }
            )
        else:
            self.update({"product_packaging_qty": 0})
        if self.product_packaging:
            return self._check_package()

    @api.onchange("product_packaging_qty")
    def _onchange_product_packaging_qty(self):
        if self.product_packaging_qty and self.product_packaging:
            self.update(self._prepare_product_packaging_qty_values())

    @api.onchange("product_uom_qty", "product_uom")
    def onchange_quantity(self):
        res = super().onchange_quantity()
        if not res:
            res = self._check_package()
        return res

    def _check_package(self):
        default_uom = self.product_id.uom_id
        pack = self.product_packaging
        qty = self.product_qty
        q = default_uom._compute_quantity(pack.qty, self.product_uom)
        if qty and q and round(qty % q, 2):
            newqty = qty - (qty % q) + q
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "This product is packaged by %.2f %s. You should use %.2f %s."
                    )
                    % (pack.qty, default_uom.name, newqty, self.product_uom.name),
                },
            }
        return {}
