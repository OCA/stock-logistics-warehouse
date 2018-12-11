# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    block_stock_entrance = fields.Boolean(
        help="if this box is checked, putting stock in this location won't be "
             "allowed. Usually used for virtual location, which has children")
