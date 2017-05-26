# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    reason = fields.Char('Reason',
                         help='Type in a reason for the '
                         'product quantity change')

    @api.multi
    def change_product_qty(self):
        if self.reason:
            this = self.with_context(change_quantity_reason=self.reason)
            return super(StockChangeProductQty, this).change_product_qty()
        return super(StockChangeProductQty, self).change_product_qty()
