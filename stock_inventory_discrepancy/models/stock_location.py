# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    discrepancy_threshold = fields.Float(
        string='Maximum Discrepancy Rate Threshold',
        digits=(3, 2),
        help="Maximum Discrepancy Rate allowed for any product when doing "
             "an Inventory Adjustment. Thresholds defined in Locations have "
             "preference over Warehouse's ones.")
