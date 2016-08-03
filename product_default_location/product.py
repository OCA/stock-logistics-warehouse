# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class product_product(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'default_location_id': fields.many2one('stock.location',
                                               string='Default Location',
                                               required=False),
        }
