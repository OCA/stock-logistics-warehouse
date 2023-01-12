# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "stock.product.secondary.unit.mixin"]
    _name = "product.template"

    stock_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        domain="[('product_tmpl_id', '=', id), ('product_id', '=', False)]",
        string="Second unit for inventory",
    )
