# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    product_cost = fields.Float(
        related="product_id.standard_price", string="Product Cost"
    )
