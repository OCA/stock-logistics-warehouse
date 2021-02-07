# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _default_product_purchase_uom_id(self):
        return self.env.ref("uom.product_uom_unit")

    packaging_id = fields.Many2one("product.packaging", "Packaging")
    product_qty_needed = fields.Float(
        "Quantity Needed", digits="Product Unit of Measure",
    )
    product_purchase_qty = fields.Float(
        "Purchase quantity",
        digits="Product Unit of Measure",
        required=True,
        default=lambda *a: 1.0,
    )
    product_purchase_uom_id = fields.Many2one(
        "uom.uom",
        "Purchase Unit of Measure",
        required=True,
        default=_default_product_purchase_uom_id,
    )
    product_qty = fields.Float(
        compute="_compute_product_qty",
        string="Quantity",
        inverse="_inverse_product_qty",
        store=True,
        readonly=False,
    )

    def _get_product_seller(self):
        self.ensure_one()
        return self.product_id._select_seller(
            partner_id=self.order_id.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order.date(),
            uom_id=self.product_uom,
        )

    @api.depends(
        "product_purchase_uom_id",
        "product_purchase_qty",
        "product_purchase_uom_id.category_id",
    )
    def _compute_product_qty(self):
        """
        Compute the total quantity
        """
        uom_categories = self.mapped("product_purchase_uom_id.category_id")
        uom_obj = self.env["uom.uom"]
        to_uoms = uom_obj.search(
            [("category_id", "in", uom_categories.ids), ("uom_type", "=", "reference")]
        )
        uom_by_category = {to_uom.category_id: to_uom for to_uom in to_uoms}
        for line in self:
            if line.display_type:
                line.product_qty = 0
                continue
            line.product_qty = line.product_purchase_uom_id._compute_quantity(
                line.product_purchase_qty,
                uom_by_category.get(line.product_purchase_uom_id.category_id),
            )

    def _inverse_product_qty(self):
        """ If product_quantity is set compute the purchase_qty
        """
        uom_categories = self.mapped("product_purchase_uom_id.category_id")
        uom_obj = self.env["uom.uom"]
        from_uoms = uom_obj.search(
            [("category_id", "in", uom_categories.ids), ("uom_type", "=", "reference")]
        )
        uom_by_category = {from_uom.category_id: from_uom for from_uom in from_uoms}
        for line in self:
            purchase_qty = line.product_qty
            if line.product_id:
                supplier = line._get_product_seller()
                if supplier:
                    product_purchase_uom = supplier.min_qty_uom_id
                    from_uom = uom_by_category.get(
                        line.product_purchase_uom_id.category_id
                    )
                    purchase_qty = from_uom._compute_quantity(
                        line.product_qty, product_purchase_uom
                    )
                    line.product_purchase_uom_id = product_purchase_uom.id
            line.product_purchase_qty = purchase_qty

    @api.onchange("packaging_id")
    def _onchange_packaging_id(self):
        if self.packaging_id:
            self.product_uom = self.packaging_id.uom_id

    @api.onchange("product_id")
    def onchange_product_id(self):
        """ set domain on product_purchase_uom_id and packaging_id
            set the first packagigng, purchase_uom and purchase_qty
        """
        domain = {}
        # call default implementation
        # restore default values
        defaults = self.default_get(["packaging_id", "product_purchase_uom_id"])
        self.packaging_id = self.packaging_id.browse(defaults.get("packaging_id", []))
        self.product_purchase_uom_id = self.product_purchase_uom_id.browse(
            defaults.get("product_purchase_uom_id", [])
        )
        # add default domains
        if self.product_id and self.partner_id:
            domain["packaging_id"] = [
                ("id", "in", self.product_id.mapped("seller_ids.packaging_id.id"),)
            ]
            domain["product_purchase_uom_id"] = [
                ("id", "in", self.product_id.mapped("seller_ids.min_qty_uom_id.id"),)
            ]
        res = super().onchange_product_id()
        if self.product_id:
            supplier = self._get_product_seller()
        else:
            supplier = self.product_id.seller_ids.browse([])
        if supplier.product_uom:
            # use the uom from the suppleir
            self.product_uom = supplier.product_uom
        if supplier.min_qty_uom_id:
            # if the supplier requires some min qty/uom,
            self.product_purchase_qty = supplier.min_qty
            self.product_purchase_uom_id = supplier.min_qty_uom_id
            domain["product_purchase_uom_id"] = [
                ("id", "=", supplier.min_qty_uom_id.id)
            ]
            to_uom = self.env["uom.uom"].search(
                [
                    ("category_id", "=", supplier.min_qty_uom_id.category_id.id,),
                    ("uom_type", "=", "reference"),
                ],
                limit=1,
            )
            to_uom = to_uom and to_uom[0]
            self.product_qty = supplier.min_qty_uom_id._compute_quantity(
                supplier.min_qty, to_uom
            )
        self.packaging_id = supplier.packaging_id
        if domain:
            if not res:
                res = {}
            res.setdefault("domain", {})
            res["domain"].update(domain)
        return res

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        vals_list = super()._prepare_stock_moves(picking)
        if not self.packaging_id:
            return vals_list
        qty = 0.0
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty -= move.product_uom._compute_quantity(
                move.product_uom_qty, self.product_uom, rounding_method="HALF-UP"
            )
        for move in incoming_moves:
            qty += move.product_uom._compute_quantity(
                move.product_uom_qty, self.product_uom, rounding_method="HALF-UP"
            )
        diff_quantity = self.product_qty - qty
        for vals in vals_list:
            vals.update(
                {"product_uom_qty": diff_quantity, "product_uom": self.product_uom.id}
            )
        return vals_list

    @api.model
    def update_vals(self, vals):
        """
        When packaging_id is set, uom_id is readonly,
        so we need to reset the uom value in the vals dict
        """
        if vals.get("packaging_id"):
            vals["product_uom"] = (
                self.env["product.packaging"].browse(vals["packaging_id"]).uom_id.id
            )
        return vals

    @api.model
    def update_vals_list(self, vals_list):
        for vals in vals_list:
            self.update_vals(vals)
        return vals_list

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "product_qty" not in vals and "product_purchase_qty" in vals:
                # compute product_qty to avoid inverse computation and reset to 1
                uom_obj = self.env["uom.uom"]
                product_purchase_uom = uom_obj.browse(vals["product_purchase_uom_id"])
                to_uom = uom_obj.search(
                    [
                        ("category_id", "=", product_purchase_uom.category_id.id),
                        ("uom_type", "=", "reference"),
                    ],
                    limit=1,
                )
                vals["product_qty"] = to_uom._compute_quantity(
                    vals["product_purchase_qty"], to_uom
                )
        res = super().create(self.update_vals_list(vals_list))
        for vals in vals_list:
            if "product_qty" in vals and not self.env.context.get(
                "recomputing_product_qty"
            ):
                # Mandatory as we always want product_qty be computed
                res.with_context(recomputing_product_qty=True)._compute_product_qty()
        return res

    def write(self, vals):
        res = super().write(self.update_vals(vals))
        # Required if we want to avoid recursion as there is nothing in
        # environment that would help distinguish write call from a
        # compute
        if "product_qty" in vals and not self.env.context.get(
            "recomputing_product_qty"
        ):
            self.with_context(recomputing_product_qty=True)._compute_product_qty()
        return res
