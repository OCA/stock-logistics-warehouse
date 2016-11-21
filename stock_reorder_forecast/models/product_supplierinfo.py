# -*- coding: utf-8 -*-
# © 2013-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    purchase_multiple = fields.Float(
        'Purchase multiple',
        help="Purchase in multiples of. Used by the purchase proposal.")
    stock_period_min = fields.Integer(
        'Minimum stock', help="Minimum stock in days of turnover. Used by "
        "the purchase proposal.")
    country_id = fields.Many2one('res.country', 'Country of origin')
