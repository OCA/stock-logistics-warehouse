# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", related="company_id.currency_id"
    )
    estimated_value = fields.Float(compute="_compute_estimated_value", store=True)

    @api.depends("quantity", "product_id.standard_price")
    def _compute_estimated_value(self):
        for record in self:
            record.estimated_value = record.quantity * record.product_id.standard_price
