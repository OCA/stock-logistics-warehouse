# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", related="company_id.currency_id"
    )
    adjustment_cost = fields.Monetary(
        string="Adjustment cost", compute="_compute_adjustment_cost", store=True
    )

    @api.depends("inventory_diff_quantity", "product_id.standard_price")
    def _compute_adjustment_cost(self):
        for record in self:
            record.adjustment_cost = False
            if record.inventory_diff_quantity:
                record.adjustment_cost = (
                    record.inventory_diff_quantity * record.product_id.standard_price
                )
