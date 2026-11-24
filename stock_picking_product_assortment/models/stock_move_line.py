# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    # The detailed operations list is opened as its own action, so its product
    # domain cannot read the picking through ``parent``.
    picking_assortment_product_ids = fields.Many2many(
        related="picking_id.assortment_product_ids",
    )
    picking_has_assortment = fields.Boolean(related="picking_id.has_assortment")
