# -*- encoding: utf-8 -*-
##############################################################################
#
#    Automatic Stock Procurement by days for OpenERP
#    Copyright (C) 2012 Sergio Corato (<http://www.icstools.it>)
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

from openerp.osv import orm, fields

class stock_warehouse_orderpoint(orm.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _qty_orderpoint_days(self, cr, uid, ids, context=None):
        """Calculate quantity to create warehouse stock for n days of sales.
        (( Qty sold in days_stats * (1+forecast_gap)) / days_stats * days_warehouse)"""

        obj_product = self.pool.get('product.product')
        product_ids = tuple(obj_product.search(cr, uid, [], context=context))
        sql= """SELECT sol.product_id AS product_id, 
        (sum( product_uos_qty )/pp.days_stats*(1+pp.forecast_gap/100) * pp.days_warehouse) 
        AS quantity FROM sale_order_line sol JOIN sale_order so ON so.id = sol.order_id 
        JOIN product_product pp ON pp.id = sol.product_id 
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sol.state in ('done','confirmed') AND pt.type = 'product'
        AND sol.product_id IN %s AND date_order > (date(now()) - pp.days_stats) 
        GROUP BY sol.product_uom, sol.product_id, pp.days_stats, pp.forecast_gap,
        pp.days_warehouse;"""
        cr.execute(sql, (product_ids,))
        sql_res = cr.fetchall()
        if sql_res:
            for val in sql_res:
                if val:
                    reord_rules_ids = self.search(cr, uid, [('product_id', '=', val[0])], context=context)
                    if reord_rules_ids:
                        self.write(cr, uid, reord_rules_ids, {'product_max_qty': val[1]}, context=context)
        return True

class product_product(orm.Model):
    _inherit = "product.product"

    _columns = {
        'days_warehouse': fields.integer('Days of needed warehouse stock'),
        'days_stats': fields.integer('Days of sale statistics'),
        'forecast_gap': fields.float('Expected sales variation (percent +/-)', digits=(6,3)),
        }
