# Copyright 2017-2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po, supplier):
        vals = super(ProcurementRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier)
        if values.get('stock_request_id', False):
            aa = self.env['stock.request'].browse(
                values['stock_request_id']).analytic_account_id
            if aa:
                vals['account_analytic_id'] = aa.id
        return vals

    def _update_purchase_order_line(self, product_id, product_qty, product_uom,
                                    values, line, partner):
        vals = super(ProcurementRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner)
        if values.get('stock_request_id', False):
            aa = self.env['stock.request'].browse(
                values['stock_request_id']).analytic_account_id
            if aa:
                vals['account_analytic_id'] = aa.id
        return vals
