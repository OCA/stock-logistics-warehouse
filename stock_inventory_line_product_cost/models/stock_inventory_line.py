# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInventoryLine(models.Model):

    _inherit = "stock.inventory.line"

    product_cost = fields.Float(
        related="product_id.standard_price", string="Product Cost"
    )
