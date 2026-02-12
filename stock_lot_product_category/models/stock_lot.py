# Copyright 2026 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    product_category_id = fields.Many2one(
        related="product_id.categ_id",
        store=True,
        readonly=True,
    )
