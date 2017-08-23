# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    discrepancy_threshold = fields.Float(
        string='Maximum Discrepancy Rate Threshold',
        digits=(3, 2),
        help="Maximum Discrepancy Rate allowed for any product when doing "
             "an Inventory Adjustment. Threshold defined in involved Location "
             "has preference.")
