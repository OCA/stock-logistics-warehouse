# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    from_default_level_packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        related="product_id.from_default_level_packaging_id",
    )
