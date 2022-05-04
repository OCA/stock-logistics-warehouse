# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockAbc(models.Model):
    _name = "stock.abc"
    _description = "Stock ABC"

    name = fields.Char(required=True)
    count = fields.Integer("Count Per Year", required=True)
    product_ids = fields.One2many("product.product", "abc_id", string="Products")
