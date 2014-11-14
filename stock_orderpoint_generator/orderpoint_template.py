# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher, Matthieu Dietrich (Camptocamp)
#    Copyright 2012-2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

""" Template of order point object """

from openerp.osv.orm import Model, fields
from .base_product_config_template import BaseProductConfigTemplate


class OrderpointTemplate(BaseProductConfigTemplate, Model):
    """ Template for orderpoints

    Here we use same model as stock.warehouse.orderpoint but set product_id
    as non mandatory as we cannot remove it. This field will be ignored.

    This has the advantage the advantage of ensuring that the order point
    and the order point template have the same fields.

    _table is redefined to separate templates from orderpoints
    """
    _name = 'stock.warehouse.orderpoint.template'

    _inherit = 'stock.warehouse.orderpoint'
    _table = 'stock_warehouse_orderpoint_template'
    _clean_mode = 'deactivate'

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            'Product',
            required=False,
            ondelete='cascade',
            domain=[('type', '=', 'product')]),
    }

    def _get_ids_2_clean(self, cr, uid, template_br, product_ids,
                         context=None):
        """ hook to select model specific objects to clean
        return must return a list of id"""
        model_obj = self._get_model()
        ids_to_del = model_obj.search(cr, uid,
                                      [('product_id', 'in', product_ids)],
                                      context=context)
        return ids_to_del

    def _check_product_uom(self, cr, uid, ids, context=None):
        '''
        Overwrite constraint _check_product_uom
        '''
        return True

    _constraints = [
        (_check_product_uom,
         'Overriding constraint',
         ['product_id', 'product_uom']),
    ]
