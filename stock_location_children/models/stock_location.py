# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    children_ids = fields.Many2many(
        'stock.location',
        'stock_location_children_ids',
        'parent_id',
        'children_id',
        compute='_compute_children_ids',
        store=True,
        help='All the children (multi-level) stock location of this location',
    )

    @api.depends('child_ids', 'child_ids.children_ids')
    def _compute_children_ids(self):
        query = """SELECT sub.id, ARRAY_AGG(sl2.id) AS children
            FROM stock_location sl2,
            (
            SELECT id, parent_path
            FROM stock_location sl
            ) sub
            WHERE sl2.parent_path LIKE sub.parent_path || '%%'
            AND sl2.id != sub.id
            AND sub.id IN %s
            GROUP BY sub.id;
        """
        self.env.cr.execute(query, (tuple(self.ids),))
        rows = self.env.cr.dictfetchall()
        for loc in self:
            all_ids = []
            for row in rows:
                if row.get('id') == loc.id:
                    all_ids = row.get('children')
                    break
            if all_ids:
                loc.children_ids = [(6, 0, all_ids)]
            else:
                loc.children_ids = [(5, 0, 0)]
