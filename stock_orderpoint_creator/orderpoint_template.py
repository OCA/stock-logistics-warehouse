# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher (Camptocamp)
#    Copyright 2012 Camptocamp SA
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

from osv import osv, fields
from base_product_config_template import BaseProductConfigTemplate

class OrderpointTemplate(BaseProductConfigTemplate, osv.osv_memory):
    """ Template for orderpoints """
    _name = 'stock.warehouse.orderpoint.template'

    _inherit = 'stock.warehouse.orderpoint'
    _table = 'stock_warehouse_orderpoint_template'

    _columns = {
        'product_id': fields.many2one('product.product',
                                      'Product',
                                      required=False,
                                      ondelete='cascade',
                                      domain=[('type','=','product')]),
    }

    def _get_ids_2_clean(
            self, cursor, uid, template_id, product_ids, context=None):
        """ hook to select model specific objects to clean 
        return must return a list of id"""
        model_obj = self._get_model()
        (warehouse_id, warehouse_name) = self.read(
                cursor, uid, template_id, ['warehouse_id'])['warehouse_id']
        search_args = [('warehouse_id', '=', warehouse_id),
                       ('product_id', 'in', product_ids)]

        ids2clean = model_obj.search(cursor, uid, search_args, context=context)
        return ids2clean

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
