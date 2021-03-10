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
            stock_request = self.env["stock.request"].browse(values['stock_request_id'])
            vals['stock_request_ids'] = [(4, stock_request.id)]
            if stock_request.analytic_account_id:
                vals['account_analytic_id'] = stock_request.analytic_account_id.id
            if stock_request.analytic_tag_ids:
                vals['analytic_tag_ids'] = [
                    (4, tag.id) for tag in stock_request.analytic_tag_ids
                ]
        return vals

    def _update_purchase_order_line(self, product_id, product_qty, product_uom,
                                    values, line, partner):
        vals = super(StockRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner)
        if 'stock_request_id' in values:
            vals['stock_request_ids'] = [(4, values['stock_request_id'])]
        return vals
