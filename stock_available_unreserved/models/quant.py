# Copyright 2018 Camptocamp SA
# Copyright 2016 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    contains_unreserved = fields.Boolean(
        string="Contains unreserved products",
        compute="_compute_contains_unreserved",
        store=True,
    )

    unreserved_quantity = fields.Float(
        string="Unreserved quantity",
        compute="_compute_unreserved_quantity",
        store=True,
    )

    @api.depends('unreserved_quantity')
    def _compute_contains_unreserved(self):
        for record in self:
            record.contains_unreserved = record.unreserved_quantity > 0

    @api.depends('quantity', 'reserved_quantity')
    def _compute_unreserved_quantity(self):
        for rec in self:
            rec.unreserved_quantity = rec.quantity - rec.reserved_quantity
