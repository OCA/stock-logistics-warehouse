# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po, partner):
        vals = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner)
        # If the procurement was run directly by a reordering rule.
        if 'orderpoint_id' in values:
            vals['orderpoint_ids'] = [
                (4, values['orderpoint_id'].id)]
        # If the procurement was run by a stock move.
        elif 'orderpoint_ids' in values:
            vals['orderpoint_ids'] = [(4, o.id)
                                      for o in values['orderpoint_ids']]
        return vals

    def _update_purchase_order_line(self, product_id, product_qty, product_uom,
                                    values, line, partner):
        vals = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner)
        if 'orderpoint_id' in values:
            vals['orderpoint_ids'] = [
                (4, values['orderpoint_id'].id)]
        # If the procurement was run by a stock move.
        elif 'orderpoint_ids' in values:
            vals['orderpoint_ids'] = [(4, o.id)
                                      for o in values['orderpoint_ids']]
        return vals
