# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
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
from openerp.osv.orm import Model, fields
import decimal_precision as dp

class product_product(Model):
    _inherit = "product.product"

    def _compute_configurable_level(self, cursor, uid, pids, field_name, args, context=None):
        """We compute a custom stock level"""
        # we do not override _product_available once agin to avoid MRO troubles
        conf_obj =  self.pool.get('stock.level.configuration')
        prod_obj = self.pool.get('product.product')
        conf_list = []
        conf_ids = conf_obj.search(cursor, uid, [])
        for conf in conf_obj.browse(cursor, uid, conf_ids):
            conf_list.append((conf.stock_location_id.id, conf.product_field.name))
        if not isinstance(pids, list):
            pids = [pids]
        res =  dict.fromkeys(pids, 0.0)
        for conf in conf_list:
            local_context = context.copy()
            local_context['location'] = [conf[0]]
            interm = prod_obj._product_available(cursor, uid, pids, field_names=[conf[1]], arg=False, context=local_context)
            for key, val in interm.items():
                res.setdefault(key, 0.0) # this should not be usefull but we never know
                res[key] += val.get(conf[1], 0.0)
        return res

    
    _columns = {'configurable_stock_level': fields.function(_compute_configurable_level,
                                                            type='float',
                                                            digits_compute=dp.get_precision('Product UoM'),
                                                            string='Custom level')}

                

