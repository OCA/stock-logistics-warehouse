# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import operator

from odoo import api, fields, models
from odoo.fields import Command


class StockLocation(models.Model):

    _inherit = "stock.location"

    children_ids = fields.Many2many(
        comodel_name="stock.location",
        relation="stock_location_children_ids",
        column1="parent_id",
        column2="children_id",
        compute="_compute_children_ids",
        store=True,
        # Don't put recursive here as the query in compute method is sufficent
        help="All the children (multi-level) stock location of this location",
    )

    @api.depends("child_ids", "children_ids.child_ids")
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
        self.flush_model(["location_id", "child_ids"])
        self.env.cr.execute(query, (tuple(self.ids),))
        rows = self.env.cr.dictfetchall()
        result_by_location = dict(zip(map(operator.itemgetter("id"), rows), rows))
        for loc in self:
            children = result_by_location.get(loc.id, {}).get("children")
            if children:
                loc.children_ids = [Command.set(children)]
            else:
                loc.children_ids = [Command.clear()]
