# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    discrepancy_threshold = fields.Float(
        string='Maximum Discrepancy Rate Threshold')
