# Copyright 2019 Eficent Business, IT Consulting Services, S.L., Ecosoft
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, values, group_id):
        vals = super()._get_stock_move_values(
            product_id, product_qty, product_uom,
            location_id, name, origin, values, group_id)
        if 'orderpoint_id' in values:
            vals['orderpoint_ids'] = [(4, values['orderpoint_id'].id)]
        elif 'orderpoint_ids' in values:
            vals['orderpoint_ids'] = [(4, o.id)
                                      for o in values['orderpoint_ids']]
        return vals
