# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    stock_amount = fields.Integer(
        compute='_compute_location_amount', search='_search_location_amount'
    )

    @api.multi
    def _search_location_amount(self, operator, value):
        if operator not in ('=', '!=', '<', '<=', '>', '>='):
            return []
        # pylint: disable=sql-injection
        self.env.cr.execute(
            """
            SELECT loc.id FROM stock_location loc
            LEFT OUTER JOIN stock_quant quant ON loc.id = quant.location_id
            GROUP BY loc.id
            HAVING coalesce(sum(quantity), 0) %s %%s;"""
            % operator,
            (value,),
        )
        ids = [row[0] for row in self.env.cr.fetchall()]
        return [('id', 'in', ids)]

    @api.multi
    def _compute_location_amount(self):
        self.env.cr.execute(
            """
            SELECT location_id, sum(quantity)
            FROM stock_quant
            WHERE location_id IN %s
            GROUP BY location_id;
        """,
            (tuple(self.ids),),
        )
        totals = dict(self.env.cr.fetchall())
        for location in self:
            location.stock_amount = totals.get(location.id, 0)
