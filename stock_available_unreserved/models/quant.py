# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    unreserved_quantity = fields.Float(
        string="Unreserved quantity",
        compute="_compute_unreserved_quantity",
        store=True,
    )

    @api.depends('quantity', 'reserved_quantity')
    def _compute_unreserved_quantity(self):
        for rec in self:
            rec.unreserved_quantity = rec.quantity - rec.reserved_quantity
