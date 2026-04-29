# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    product_template_attribute_value_ids = fields.Many2many(
        related="product_id.product_template_attribute_value_ids"
    )
    product_image_128 = fields.Image(related="product_id.image_128")

    def _get_lst_price(self):
        self.ensure_one()
        return self.product_id.lst_price
