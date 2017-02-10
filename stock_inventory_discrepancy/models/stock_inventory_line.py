# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.one
    def _compute_discrepancy(self):
        self. discrepancy_qty = self.product_qty - self.theoretical_qty
        if self.theoretical_qty:
            self.discrepancy_percent = 100 * (abs(
                self.product_qty - self.theoretical_qty)) \
                / self.theoretical_qty
        elif not self.theoretical_qty and self.product_qty:
            self.discrepancy_percent = 100.0

    @api.one
    def _get_discrepancy_threshold(self):
        wh_id = self.location_id.get_warehouse(self.location_id)
        wh = self.env['stock.warehouse'].browse(wh_id)
        if self.location_id.discrepancy_threshold > 0.0:
            self.discrepancy_threshold = self.location_id.discrepancy_threshold
        elif wh.discrepancy_threshold > 0.0:
            self.discrepancy_threshold = wh.discrepancy_threshold
        else:
            self.discrepancy_threshold = False

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
        compute=_get_discrepancy_threshold)
