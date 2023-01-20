# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockReservation(models.Model):
    _inherit = "stock.reservation"

    sale_line_id = fields.Many2one(
        "sale.order.line", string="Sale Order Line", ondelete="cascade", copy=False
    )
    sale_id = fields.Many2one(
        "sale.order", string="Sale Order", related="sale_line_id.order_id"
    )

    def release_reserve(self):
        for rec in self:
            rec.sale_line_id = False
        return super().release_reserve()
