# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons import decimal_precision as dp
from odoo import api, fields, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    discrepancy_amount = fields.Monetary(
        string="Amount Discrepancy",
        compute="_compute_discrepancy_amount",
        currency_field="company_currency_id",
        help="The difference between the actual qty counted and the "
             "theoretical quantity on hand expressed in the cost amount.",
        digits=dp.get_precision("Product Unit of Measure"), default=0)
    discrepancy_amount_threshold = fields.Monetary(
        string="Amount Threshold",
        currency_field="company_currency_id",
        help="Maximum Discrepancy Amount Threshold",
        compute="_compute_discrepancy_amount_threshold")
    company_currency_id = fields.Many2one(
        string="Company Currency",
        comodel_name="res.currency",
        related="inventory_id.company_id.currency_id",
        readonly=False,
    )

    @api.multi
    @api.depends("theoretical_qty", "product_qty")
    def _compute_discrepancy_amount(self):
        for line in self:
            discrepancy_qty = line.product_qty - line.theoretical_qty
            cost = line.product_id.standard_price
            line.discrepancy_amount = discrepancy_qty * cost

    @api.multi
    def _compute_discrepancy_amount_threshold(self):
        for line in self:
            whs = line.location_id.get_warehouse()
            if line.location_id.discrepancy_amount_threshold > 0.0:
                line.discrepancy_amount_threshold = line.location_id.\
                    discrepancy_amount_threshold
            elif whs.discrepancy_amount_threshold > 0.0:
                line.discrepancy_amount_threshold = \
                    whs.discrepancy_amount_threshold
            else:
                line.discrepancy_amount_threshold = False

    @api.multi
    def _has_over_discrepancy(self):
        res = super()._has_over_discrepancy()
        return res or abs(
            self.discrepancy_amount) > self.discrepancy_amount_threshold > 0
