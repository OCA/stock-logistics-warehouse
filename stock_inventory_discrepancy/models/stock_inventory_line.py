# Copyright 2017-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    discrepancy_qty = fields.Float(
        string="Discrepancy",
        compute="_compute_discrepancy",
        help="The difference between the actual qty counted and the "
        "theoretical quantity on hand.",
        digits="Product Unit of Measure",
        default=0,
        compute_sudo=True,
    )
    discrepancy_percent = fields.Float(
        string="Discrepancy percent (%)",
        compute="_compute_discrepancy",
        digits=(3, 2),
        help="The discrepancy expressed in percent with theoretical quantity "
        "as basis",
        group_operator="avg",
        store=True,
        compute_sudo=True,
    )
    discrepancy_threshold = fields.Float(
        string="Threshold (%)",
        digits=(3, 2),
        help="Maximum Discrepancy Rate Threshold",
        compute="_compute_discrepancy_threshold",
    )
    has_over_discrepancy = fields.Boolean(
        compute="_compute_has_over_discrepancy",
    )

    @api.depends("theoretical_qty", "product_qty")
    def _compute_discrepancy(self):
        for line in self:
            line.discrepancy_qty = line.product_qty - line.theoretical_qty
            if line.theoretical_qty:
                line.discrepancy_percent = 100 * abs(
                    (line.product_qty - line.theoretical_qty) / line.theoretical_qty
                )
            elif not line.theoretical_qty and line.product_qty:
                line.discrepancy_percent = 100.0
            else:
                line.discrepancy_percent = 0.0

    def _compute_discrepancy_threshold(self):
        for line in self:
            whs = line.location_id.get_warehouse()
            if line.location_id.discrepancy_threshold > 0.0:
                line.discrepancy_threshold = line.location_id.discrepancy_threshold
            elif whs.discrepancy_threshold > 0.0:
                line.discrepancy_threshold = whs.discrepancy_threshold
            else:
                line.discrepancy_threshold = False

    def _compute_has_over_discrepancy(self):
        for rec in self:
            rec.has_over_discrepancy = rec._has_over_discrepancy()

    def _has_over_discrepancy(self):
        return self.discrepancy_percent > self.discrepancy_threshold > 0
