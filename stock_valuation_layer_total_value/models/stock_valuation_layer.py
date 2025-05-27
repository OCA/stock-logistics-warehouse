# Copyright 2022 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    total_value_with_additional_costs = fields.Float(
        string="Total value (with additional costs)",
        compute="_compute_original_layer_values",
        help="This is the sum of the total value's layer and total value of child layers",  # noqa: E501
        store=True,
    )
    unit_price_with_extra_cost = fields.Float(
        string="New unit price (with additional costs)",
        compute="_compute_original_layer_values",
        help="This is the unit cost after the additional costs are added",
        store=True,
    )

    @api.depends("stock_valuation_layer_ids")
    def _compute_original_layer_values(self):
        for rec in self:
            children = rec.stock_valuation_layer_ids
            children_value = sum(children.mapped("value")) if children else 0.0
            total_value = rec.value + children_value
            rec.total_value_with_additional_costs = total_value
            rec.unit_price_with_extra_cost = (
                total_value / rec.quantity if rec.quantity else rec.unit_cost
            )
