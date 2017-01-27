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

    @api.one
    def _compute_discrepancy_percentage(self):
        if self.theoretical_qty:
            self.discrepancy_percentage = (abs(
                self.product_qty - self.theoretical_qty)) \
                                          / self.theoretical_qty

    discrepancy_qty = fields.Float(string='Discrepancy',
                                   compute=_compute_discrepancy)
    discrepancy_percentage = fields.Float(
        string='Discrepancy rate',
        compute=_compute_discrepancy_percentage)
