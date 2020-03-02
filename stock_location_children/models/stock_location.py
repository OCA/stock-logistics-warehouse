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
        for loc in self:
            if not loc.child_ids.mapped('child_ids'):
                all_children = loc.child_ids
            else:
                all_children = loc.child_ids | loc.child_ids.children_ids
            loc.children_ids = all_children
