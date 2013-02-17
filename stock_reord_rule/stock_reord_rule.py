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

from osv import osv, fields

class stock_warehouse_orderpoint(osv.osv):
    _inherit = "stock.warehouse.orderpoint"

    def _qty_orderpoint_days(self, cr, uid, ids, context=None):
        """Calculate quantity to create warehouse stock for n days of sales.
        integer (( Qty sold in days_stats * (1+forecast_gap)) / days_stats * days_warehouse)"""

        res = {}
        obj_product = self.pool.get('product.product')
        product_ids = tuple(obj_product.search(cr, uid, []))
        if len(product_ids) > 1:
            sql= """SELECT sol.product_id AS product_id, (sum( product_uos_qty )/pp.days_stats*(1+pp.forecast_gap/100) * pp.days_warehouse) AS quantity FROM sale_order_line sol JOIN sale_order so ON so.id = sol.order_id JOIN product_product pp ON pp.id = sol.product_id WHERE sol.state in ('done','confirmed') AND sol.product_id IN {product_ids} AND date_order > (date(now()) - pp.days_stats) GROUP BY sol.product_uom, sol.product_id, pp.days_stats, pp.forecast_gap, pp.days_warehouse;""".format(product_ids=product_ids)
            cr.execute(sql)
            sql_res = cr.fetchall()
            for val in sql_res:
                if val:
                    reord_rules_ids = self.search(cr, uid, [('product_id','=', val[0])])
                    if reord_rules_ids:
                        res['product_max_qty'] = val[1]
                        self.write(cr, uid, reord_rules_ids, res)
        return True

stock_warehouse_orderpoint()

class product_product(osv.osv):
    _inherit = "product.product"

    _columns = {
        'days_warehouse': fields.integer('Nr of days of warehouse stock'),
        'days_stats':fields.integer('Nr of days on which calculate stats'),
        'forecast_gap':fields.float('Forecast gap%', digits=(6,int(3))),
        }

product_product()
