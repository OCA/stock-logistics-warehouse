# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


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
