# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.sql import SQL
from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.multi
    def write(self, vals):
        forced_inventory_date = self.env.context.get(
            'forced_inventory_date', False)
        if 'date' in vals and forced_inventory_date:
            vals['date'] = forced_inventory_date
        return super(StockMoveLine, self).write(vals)

    @api.model
    def create(self, vals):
        forced_inventory_date = self.env.context.get(
            'forced_inventory_date', False)
        if 'date' in vals and forced_inventory_date:
            vals['date'] = forced_inventory_date
        return super(StockMoveLine, self).create(vals)

    @api.model
    def get_lot_qty_at_date_in_location(self, product, location, date, lot=None):
        sql = SQL(r"""
            SELECT
                qty
                , lot_id
            FROM
                (
                SELECT
                    COALESCE(incoming.qty_done, 0)
                      - COALESCE(outgoing.qty_done, 0)  AS qty
                    , incoming.lot_id
                FROM
                    (
                    SELECT
                        sum(qty_done) AS qty_done
                        , lot_id
                    FROM
                        stock_move_line sml
                    WHERE
                        state = 'done'
                        AND product_id = %s
                        AND location_dest_id = %s
                        AND date < %s {lot_clause}
                    GROUP BY
                        lot_id
                    ) incoming
                LEFT OUTER JOIN
                    (
                    SELECT
                        sum(qty_done) AS qty_done, lot_id
                    FROM
                        stock_move_line sml
                    WHERE
                        state = 'done'
                        AND product_id = %s
                        AND location_id = %s
                        AND date < %s {lot_clause}
                    GROUP BY
                        lot_id
                    ) outgoing
                ON
                    incoming.lot_id = outgoing.lot_id
                ) balance
            WHERE
                balance.qty != 0;
        """)
        base_params = [product.id, location.id, date]
        lot_clause = SQL(r"""""")
        if lot is not None:
            lot_clause = SQL(r"""AND lot_id = %s""")
            base_params.append(lot.id)
        sql = sql.format(lot_clause=lot_clause)
        params = tuple(base_params) * 2
        self.env.cr.execute(sql, tuple(params))
        return self.env.cr.dictfetchall()
