# -*- coding: utf-8 -*-
# © 2013-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    stock_period_min = fields.Integer(
        'Minimum stock', help="Minimum stock in days of turnover. Used by the "
        "purchase proposal.")
    stock_period_max = fields.Integer(
        'Maximium stock', help="Maximum stock in days turnover to resupply "
        "for. Used by the purchase proposal.")
    turnover_period = fields.Integer(
        'Turnover period', help="Turnover days to calculate average turnover "
        "per day. Used by the purchase proposal.")
