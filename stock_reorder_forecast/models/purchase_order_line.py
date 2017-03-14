# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from openerp.tools.float_utils import float_round


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # NOTE in 9.0 the onchanges have finally been ported to new API

    def _get_stock_period_max(self):
        if self.product_id.stock_period_max > 0:
            res = self.product_id.stock_period_max
        elif self.partner_id.stock_period_max > 0:
            res = self.partner_id.stock_period_max
        elif self.product_id.product_tmpl_id.categ_id.stock_period_max > 0:
            res = self.product_id.product_tmpl_id.categ_id.stock_period_max
        else:
            # TODO understand how to create integer parameters
            res = float(self.env['ir.config_parameter'].search(
                [('key', '=', 'default_period_max')])[0].value)
        return res

    def _get_purchase_multiple(self):
        for supplier in self.product_id.seller_ids:
            if supplier.purchase_multiple:
                return supplier.purchase_multiple
        return float(self.env['ir.config_parameter'].search(
            [('key', '=', 'default_purchase_multiple')])[0].value)

    @api.onchange('product_id')
    def onchange_product_id(self):
        #  This will trigger also _onchange_quantity and _suggest_quantity
        #  Because of the purchase proposal we calculate the qty when set to 0"
        if self.product_qty == 0 and self.product_id:
            product = self.product_id
            stock_period_max = self._get_stock_period_max()
            purchase_multiple = self._get_purchase_multiple()
            stock = product.virtual_available
            turnover_average = product.turnover_average
            qty = float_round(
                turnover_average * stock_period_max - stock, 0
            )
            self.product_qty = int(
                (qty + purchase_multiple - 1) /
                purchase_multiple
            ) * purchase_multiple
        super(PurchaseOrderLine, self).onchange_product_id()
