# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import sql

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    stock_amount = fields.Float(
        compute="_compute_location_amount", search="_search_location_amount"
    )

    def _search_location_amount(self, operator, value):
        if operator not in ("=", "!=", "<", "<=", ">", ">="):
            return []
        query = sql.SQL(
            """
            SELECT loc.id FROM stock_location loc
            LEFT OUTER JOIN stock_quant quant ON loc.id = quant.location_id
            GROUP BY loc.id
            HAVING coalesce(sum(quantity), 0) {operator} %(value)s;""".format(
                operator=operator
            )
        )

        self.env.cr.execute(query, {"value": value})
        res = self.env.cr.fetchall()
        ids = [row[0] for row in res]
        return [("id", "in", ids)]

    def _compute_location_amount(self):
        query = sql.SQL(
            """
            SELECT location_id, sum(quantity)
            FROM stock_quant
            WHERE location_id IN %(values)s
            GROUP BY location_id;
        """
        )
        self.env.cr.execute(query, {"values": tuple(self.ids)})
        totals = dict(self.env.cr.fetchall())
        for location in self:
            location.stock_amount = totals.get(location.id, 0)
