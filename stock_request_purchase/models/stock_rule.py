# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po, supplier):
        vals = super(StockRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier)
        if 'stock_request_id' in values:
            vals['stock_request_ids'] = [(4, values['stock_request_id'])]
        return vals

    def _update_purchase_order_line(self, product_id, product_qty, product_uom,
                                    values, line, partner):
        vals = super(StockRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner)
        if 'stock_request_id' in values:
            vals['stock_request_ids'] = [(4, values['stock_request_id'])]
        return vals
