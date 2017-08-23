# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.multi
    def _compute_discrepancy(self):
        for l in self:
            l.discrepancy_qty = l.product_qty - l.theoretical_qty
            if l.theoretical_qty:
                l.discrepancy_percent = 100 * abs(
                    (l.product_qty - l.theoretical_qty) /
                    l.theoretical_qty)
            elif not l.theoretical_qty and l.product_qty:
                l.discrepancy_percent = 100.0

    @api.multi
    def _compute_discrepancy_threshold(self):
        for l in self:
            wh = l.location_id.get_warehouse()
            if l.location_id.discrepancy_threshold > 0.0:
                l.discrepancy_threshold = l.location_id.discrepancy_threshold
            elif wh.discrepancy_threshold > 0.0:
                l.discrepancy_threshold = wh.discrepancy_threshold
            else:
                l.discrepancy_threshold = False

    discrepancy_qty = fields.Float(
        string='Discrepancy',
        compute=_compute_discrepancy,
        help="The difference between the actual qty counted and the "
             "theoretical quantity on hand.")
    discrepancy_percent = fields.Float(
        string='Discrepancy percent (%)',
        compute=_compute_discrepancy,
        digits=(3, 2),
        help="The discrepancy expressed in percent with theoretical quantity "
             "as basis")
    discrepancy_threshold = fields.Float(
        string='Threshold (%)',
        digits=(3, 2),
        help="Maximum Discrepancy Rate Threshold",
        compute=_compute_discrepancy_threshold)
