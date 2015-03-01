from openerp.osv import fields, osv
from openerp.tools.sql import drop_view_if_exists


class stock_report_prodlots(osv.osv):
    _inherit = "stock.report.prodlots"

    def init(self, cr):
        drop_view_if_exists(cr, 'stock_report_prodlots')
        cr.execute("""
            create or replace view stock_report_prodlots as (
                select max(id) as id,
                    location_id,
                    product_id,
                    prodlot_id,
                    sum(qty) as qty
                from (
                    select -max(sm.id) as id,
                        sm.location_id,
                        sm.product_id,
                        sm.prodlot_id,
                        -sum(sm.product_qty /uo.factor) +
                        coalesce(lot.retained_stock, 0) as qty
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
                        sum(sm.product_qty /uo.factor) -
                        coalesce(lot.retained_stock, 0) as qty
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
                group by location_id, product_id, prodlot_id
            )""")
