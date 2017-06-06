# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from openerp.tools.sql import drop_view_if_exists


class stock_report_prodlots(orm.Model):

    """
    Override the stock.report.prodlots.

    We have to substract and add the retained value on stock_move
    that have a prodlot assigned to it. The prodlot objects should
    have a retained_stock value which is used to calculate a fake
    quantity of product.
    """

    _inherit = "stock.report.prodlots"

    def init(self, cr):
        """
        Delete and replace the previous view by this one.

        This view is an extension of the view in the module
        stock of odoo.

        file: odoo/addons/stock/report/report_stock.py
        """
        drop_view_if_exists(cr, 'stock_report_prodlots')
        cr.execute("""
            create or replace view stock_report_prodlots as (
                select max(id) as id,
                    location_id,
                    product_id,
                    prodlot_id,
                    sum(qty) - retained_stock as qty
                from (
                    select -max(sm.id) as id,
                        sm.location_id,
                        sm.product_id,
                        sm.prodlot_id,
                        -sum(sm.product_qty /uo.factor) as qty,
                        coalesce(lot.retained_stock, 0) as retained_stock
                    from stock_move as sm
                    left join stock_location sl
                        on (sl.id = sm.location_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    left join stock_production_lot lot
                        on (lot.id=sm.prodlot_id)
                    where state = 'done'
                    group by sm.location_id, sm.product_id,
                             sm.product_uom, sm.prodlot_id,
                             lot.retained_stock
                    union all
                    select max(sm.id) as id,
                        sm.location_dest_id as location_id,
                        sm.product_id,
                        sm.prodlot_id,
                        sum(sm.product_qty /uo.factor) as qty,
                        coalesce(lot.retained_stock, 0) as retained_stock
                    from stock_move as sm
                    left join stock_location sl
                        on (sl.id = sm.location_dest_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    left join stock_production_lot lot
                        on (lot.id=sm.prodlot_id)
                    where state = 'done'
                    group by sm.location_dest_id, sm.product_id,
                             sm.product_uom, sm.prodlot_id,
                             lot.retained_stock
                ) as report
                group by location_id, product_id, prodlot_id, retained_stock
            )""")
