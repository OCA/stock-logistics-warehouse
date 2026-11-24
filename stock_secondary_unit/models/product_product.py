# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = ["product.product", "stock.product.secondary.unit.mixin"]
    _name = "product.product"

    stock_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Second unit for inventory",
        readonly=False,
        domain="['|', ('product_id', '=', id),"
        "'&', ('product_tmpl_id', '=', product_tmpl_id),"
        "     ('product_id', '=', False)]",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # New variants (e.g. after adding an attribute value) get the one of
        # their template
        for vals in vals_list:
            if "stock_secondary_uom_id" in vals or not vals.get("product_tmpl_id"):
                continue
            secondary_uom = (
                self.env["product.template"]
                .browse(vals["product_tmpl_id"])
                .stock_secondary_uom_id
            )
            # A unit of a specific variant does not apply to the other ones
            if secondary_uom and not secondary_uom.product_id:
                vals["stock_secondary_uom_id"] = secondary_uom.id
        return super().create(vals_list)
